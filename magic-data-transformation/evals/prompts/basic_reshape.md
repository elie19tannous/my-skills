# Eval: Basic Reshape

## Task

You have a CSV file `quarterly_sales.csv` with the following structure:

| salesperson | region | q1_sales | q2_sales | q3_sales | q4_sales |
|-------------|--------|----------|----------|----------|----------|
| Alice       | North  | 15000    | 18000    | 22000    | 19000    |
| Bob         | South  | 12000    | 14000    | 16000    | 21000    |
| Carol       | East   | 19000    | 17000    | 20000    | 23000    |

Convert this wide-format table to long format so that each row represents one salesperson-quarter combination. The output should have columns: `salesperson`, `region`, `quarter`, `sales`.

Save the result as `sales_long.csv`.

## Expected Behaviors (for scoring)

- [ ] Agent identifies this as a melt/unpivot operation
- [ ] Agent specifies correct id_vars (salesperson, region) and value_vars (q1-q4 columns)
- [ ] Agent renames the variable/value columns to meaningful names (quarter, sales)
- [ ] Agent tracks row count change: expects 3 rows * 4 quarters = 12 output rows
- [ ] Agent validates output shape after transformation
