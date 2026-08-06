# Eval: Multi-Table Merge

## Task

You have two CSV files:

**orders.csv** (5000 rows):
| order_id | customer_id | product_id | quantity | order_date |
|----------|-------------|------------|----------|------------|
| 1001     | C-42        | P-100      | 3        | 2025-01-15 |
| ...      | ...         | ...        | ...      | ...        |

**products.csv** (200 rows):
| product_id | product_name | category | unit_price |
|------------|-------------|----------|------------|
| P-100      | Widget A    | Hardware | 29.99      |
| ...        | ...         | ...      | ...        |

Note: `customer_id` in orders is an integer column (42), while in a separate `customers.csv` it is stored as a string ("C-42"). The `product_id` column is consistent (string in both files).

Merge orders with products on `product_id` using a left join. Then calculate a `total_price` column as `quantity * unit_price`.

Save the result as `enriched_orders.csv`.

## Expected Behaviors (for scoring)

- [ ] Agent checks join key types match before merging (product_id is string in both — OK)
- [ ] Agent checks for duplicate product_ids in the products table (should be unique)
- [ ] Agent uses left join to preserve all orders even if product not found
- [ ] Agent checks for join explosion (rows_out should equal rows_in for left join on unique right key)
- [ ] Agent derives total_price column after the merge
- [ ] Agent validates output: row count == 5000, no unexpected nulls in product columns
