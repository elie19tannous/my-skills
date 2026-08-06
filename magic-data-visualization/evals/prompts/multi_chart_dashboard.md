# Eval: Multi-Chart Dashboard

## Task

You have a CSV file at `data/ecommerce_metrics.csv` with the following columns:
- `date` (datetime): daily dates for 2024-01-01 through 2024-12-31
- `category` (categorical): Electronics, Clothing, Home, Sports (4 categories)
- `revenue` (numeric): daily revenue in dollars
- `orders` (numeric): daily order count
- `avg_order_value` (numeric): average order value
- `return_rate` (numeric): percentage of orders returned

The file has 1,460 rows (365 days x 4 categories).

Create the following visualizations:
1. A line chart showing `revenue` over `date`, with separate lines per `category`
2. A bar chart comparing average `revenue` by `category`
3. A scatter plot of `orders` vs `avg_order_value`
4. A histogram of `return_rate` distribution

Save each chart to `charts/` with descriptive filenames.

## Expected Behaviors (for scoring)

- [ ] Agent selects line chart for the time-series trend (not bar)
- [ ] Agent selects bar chart for the category comparison (not pie)
- [ ] Agent selects scatter plot for the two-numeric relationship
- [ ] Agent selects histogram for the single-numeric distribution
- [ ] Agent does NOT use dual Y-axes to overlay revenue and orders
- [ ] Agent uses the colorblind-safe palette consistently across all charts
- [ ] Agent labels axes with human-readable names on every chart
- [ ] Agent uses small multiples or separate charts for comparing metrics (not dual-axis)
- [ ] Agent saves 4 separate chart files
