# Eval: Basic CSV Load

## Task

You have a CSV file at `data/sales_q4.csv` containing quarterly sales data. The file has 2,500 rows and columns: date, product_id, region, quantity, unit_price, total_revenue. Load it into a pandas DataFrame, verify the data loaded correctly, and save a checkpoint.

## Context

- The file is 1.2MB (small, no chunking needed)
- The file extension is `.csv` but you haven't verified the actual format yet
- You don't know the encoding or delimiter

## Expected Behaviors (for scoring)

- [ ] Agent detects format before loading (does not assume CSV based on extension alone)
- [ ] Agent auto-detects encoding and delimiter
- [ ] Agent loads the file into a DataFrame
- [ ] Agent validates after loading (checks row count, column types, null patterns)
- [ ] Agent reports basic statistics: row count, column count, dtypes
- [ ] Agent saves a checkpoint file with a descriptive name
