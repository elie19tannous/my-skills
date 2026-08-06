# Eval: Missing Value Handling

## Task

You have a CSV file at `data/customer_orders.csv` with 5,000 rows and columns: customer_id (int), name (text), email (text), order_total (float), order_date (date), region (categorical, 6 values), loyalty_score (float). The file has the following missing value profile:

- `order_total`: 3% missing (142 rows)
- `loyalty_score`: 18% missing (912 rows)
- `region`: 4% missing (198 rows)
- `email`: 8% missing (401 rows)

Handle the missing values appropriately for each column, validate the results, and save a checkpoint.

## Context

- The data will be used for a regional sales analysis, so `region` is critical
- `loyalty_score` is used for customer segmentation downstream
- `email` is a free-text field with no meaningful imputation possible via statistics
- No sentinel values are present — the missing values are genuine NaN

## Expected Behaviors (for scoring)

- [ ] Agent runs issue detection first to understand the full missing value picture
- [ ] Agent selects different strategies per column based on type and missing percentage
- [ ] Agent uses mean or median for `order_total` (low missing %, numeric)
- [ ] Agent uses KNN or similar correlation-preserving method for `loyalty_score` (moderate missing %, numeric)
- [ ] Agent uses mode for `region` (categorical)
- [ ] Agent drops rows or leaves NaN for `email` (text — does NOT impute with mode)
- [ ] Agent validates after imputation — checks null counts reduced, no new nulls introduced
- [ ] Agent saves a checkpoint after handling missing values
