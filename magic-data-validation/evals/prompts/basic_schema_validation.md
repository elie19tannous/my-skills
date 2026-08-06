# Eval: Basic Schema Validation

## Task

You have a CSV file `customer_orders.csv` with the following columns:
- `customer_id` (integer, should never be null)
- `name` (text)
- `email` (text, should match email pattern)
- `order_total` (numeric, should be >= 0)
- `order_date` (date string, format YYYY-MM-DD)
- `status` (categorical: "pending", "shipped", "delivered", "cancelled")

The file has 5,000 rows. Some rows have issues: a few `order_total` values are negative, some `email` fields contain "TBD", and 12 rows have null `customer_id`.

Infer the schema, validate the data against it, and produce a validation report.

## Expected Behaviors (for scoring)

- [ ] Agent infers schema from the full dataset (not just first few rows)
- [ ] Agent detects `customer_id` nulls as violations
- [ ] Agent detects negative `order_total` values as constraint violations
- [ ] Agent validates `email` column against a pattern
- [ ] Agent validates `status` column against allowed values
- [ ] Agent follows validation ordering: schema first, then constraints
- [ ] Agent produces a structured validation report (JSON or similar)
- [ ] Agent does not apply numeric rules to text columns
