# Eval: Large Dataset Profiling

## Task

You have a dataset at `data/transactions.parquet` with 5,000,000 rows and 25 columns including:
- `transaction_id` (string, unique)
- `amount` (float, range 0.01 to 500,000)
- `currency` (string, 15 unique currencies)
- `merchant_category` (string, 200+ unique categories)
- `description` (string, free-text, average 50 words)
- `customer_id` (string, 100,000 unique customers)
- `timestamp` (datetime)
- 18 additional numeric and categorical columns

Profile this dataset comprehensively. The goal is to assess data quality and identify issues before building a fraud detection model.

## Expected Behaviors (for scoring)

- [ ] Agent does NOT run `detect_all_issues.py` on the full 5M rows without `--sample-size`
- [ ] Agent samples first (e.g., 10,000 rows) for initial profiling overview
- [ ] Agent explicitly notes that sampled profiling results have uncertainty and may miss rare patterns
- [ ] Agent identifies targeted columns for full-scale profiling after reviewing sample results (e.g., `amount` for outliers, `currency` for category balance)
- [ ] Agent uses or generates a caching pattern for expensive operations (correlation matrix, TF-IDF clustering)
- [ ] Agent considers memory constraints — does not attempt to compute a 25-column correlation heatmap at full scale
- [ ] Agent reports quality score with context: 5M rows, 25 columns, fraud detection use case
- [ ] Agent profiles `description` column using text metrics (length, vocabulary) not numeric metrics
