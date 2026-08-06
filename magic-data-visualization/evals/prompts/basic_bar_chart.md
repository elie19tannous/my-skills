# Eval: Basic Bar Chart

## Task

You have a CSV file at `data/sales_by_region.csv` with the following columns:
- `region` (categorical): North, South, East, West, Central
- `total_sales` (numeric): dollar amounts ranging from 50,000 to 250,000
- `num_stores` (numeric): integer counts ranging from 5 to 25

The file has 5 rows (one per region).

Create a bar chart comparing `total_sales` across `region`. Save as `charts/sales_by_region.png`.

## Expected Behaviors (for scoring)

- [ ] Agent selects bar chart (categorical x-axis, numeric y-axis)
- [ ] Agent uses the colorblind-safe palette
- [ ] Agent labels x-axis as "Region" and y-axis as "Total Sales" (or similar human-readable labels)
- [ ] Agent includes a descriptive title
- [ ] Agent starts Y-axis at zero (does not truncate)
- [ ] Agent uses 300 DPI for the output
- [ ] Agent removes top and right spines
- [ ] Agent does NOT use a pie chart, 3D chart, or dual Y-axes
