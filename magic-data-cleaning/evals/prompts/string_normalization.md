# Eval: String Normalization

## Task

You have a CSV file at `data/product_catalog.csv` with 12,000 rows and columns: product_id, product_name, category, description, manufacturer, country_of_origin. The text columns have the following issues:

- `product_name`: 340 rows have leading/trailing whitespace, 89 rows have double spaces, 23 rows have mojibake characters (e.g., `"CafÃ© Machine"` instead of `"Cafe Machine"`)
- `category`: inconsistent casing (`"Electronics"`, `"electronics"`, `"ELECTRONICS"`) across 6 distinct categories
- `description`: 156 rows have unicode control characters, 45 rows have non-NFC-normalized unicode
- `manufacturer`: 67 rows have trailing tabs and carriage returns from a Windows export

Clean all text quality issues, validate the results, and save a checkpoint.

## Context

- The `category` column will be used for groupby aggregation, so casing must be consistent
- The `product_name` column feeds into a search index, so whitespace and encoding matter
- The `description` column is user-facing, so control characters must be removed
- You should NOT change the semantic content of any field — only fix formatting issues

## Expected Behaviors (for scoring)

- [ ] Agent identifies text quality issues before cleaning (does not blindly normalize everything)
- [ ] Agent applies trim before whitespace collapse (correct operation order)
- [ ] Agent fixes mojibake patterns in `product_name` (encoding normalization)
- [ ] Agent normalizes casing in `category` for consistency (e.g., all lowercase or title case)
- [ ] Agent removes control characters from `description` while preserving newlines/tabs
- [ ] Agent applies NFC unicode normalization
- [ ] Agent does NOT alter semantic content (no word changes, no translation)
- [ ] Agent validates after normalization — confirms issue counts dropped to zero
- [ ] Agent saves a checkpoint
