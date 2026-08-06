# Eval: Complex Transformation Pipeline

## Task

You have three CSV files:

**transactions.csv** (50,000 rows):
| txn_id | store_id | product_id | quantity | amount | txn_date   |
|--------|----------|------------|----------|--------|------------|
| T-001  | 5        | 101        | 2        | 59.98  | 2025-03-01 |
| ...    | ...      | ...        | ...      | ...    | ...        |

Note: `store_id` is an integer, `product_id` is an integer.

**stores.csv** (50 rows):
| store_id | store_name   | region  | city       |
|----------|-------------|---------|------------|
| 5        | Downtown    | West    | Portland   |
| ...      | ...         | ...     | ...        |

Note: `store_id` is a string ("5").

**products.csv** (500 rows):
| product_id | name        | category    | cost  |
|------------|-------------|-------------|-------|
| 101        | Widget Pro  | Electronics | 19.99 |
| ...        | ...         | ...         | ...   |

Build a pipeline that:
1. Joins transactions with stores on `store_id` (note the type mismatch)
2. Joins the result with products on `product_id`
3. Filters to only transactions in Q1 2025 (January-March)
4. Derives a `profit` column: `amount - (quantity * cost)`
5. Derives a `margin_tier` column: "high" if profit margin > 50%, "medium" if > 20%, "low" otherwise
6. Aggregates by `region` and `category`: total revenue (sum of amount), total profit, transaction count
7. Pivots the aggregation so each category is a column, regions are rows, and values are total revenue

Save intermediate checkpoints and the final result as `regional_category_revenue.csv`.

## Expected Behaviors (for scoring)

- [ ] Agent casts store_id to matching type before first join (int to str or str to int)
- [ ] Agent checks cardinality on both join keys before merging
- [ ] Agent applies transforms in correct order: type cast -> join -> join -> filter -> derive -> aggregate -> pivot
- [ ] Agent uses np.where chain for margin_tier conditional logic
- [ ] Agent aggregates at (region, category) grain and verifies group count
- [ ] Agent deduplicates or handles potential pivot conflicts before pivoting
- [ ] Agent validates final output shape and data integrity
- [ ] Agent saves at least one intermediate checkpoint
