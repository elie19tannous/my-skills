# Eval: Constraint Checking

## Task

You have a dataset `employee_records.csv` with 10,000 rows and the following columns:
- `employee_id` (integer, unique, not null)
- `department` (categorical: "Engineering", "Sales", "Marketing", "HR", "Finance")
- `hire_date` (date string, YYYY-MM-DD)
- `termination_date` (date string, YYYY-MM-DD, nullable -- null means still employed)
- `salary` (numeric, range 30000-500000)
- `manager_id` (integer, nullable -- null for top-level managers)
- `performance_notes` (free text, nullable)
- `status` (categorical: "active", "inactive", "on_leave")

Known issues in the data:
- 45 rows have `termination_date` before `hire_date`
- 8 rows have `salary` = 0 (placeholder values)
- `performance_notes` contains sentinel values: "N/A" (200 rows), "TBD" (50 rows), single spaces (15 rows)
- 3 rows have `department` values not in the allowed set ("Ops", "IT")
- `manager_id` references `employee_id` values that do not exist in the dataset (referential integrity issue)

Define constraints and validate the dataset. Report all violations with counts and sample values.

## Expected Behaviors (for scoring)

- [ ] Agent defines cross-column constraint: `hire_date` < `termination_date`
- [ ] Agent defines range constraint for `salary` and catches the zero-salary placeholders
- [ ] Agent defines enum constraint for `department` and catches "Ops" and "IT"
- [ ] Agent runs content validation on `performance_notes` and catches sentinels ("N/A", "TBD", spaces)
- [ ] Agent does NOT apply numeric validation to `performance_notes`
- [ ] Agent checks referential integrity on `manager_id` -> `employee_id`
- [ ] Agent follows schema -> constraints -> content ordering
- [ ] Agent produces a report with violation counts and sample values per column
