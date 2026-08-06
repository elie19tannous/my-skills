# Eval: Basic Pattern Detection

## Task

You have a CSV file at `data/sales_records.csv` with the following columns:
- `date` (YYYY-MM-DD)
- `region` (North, South, East, West)
- `product` (A, B, C)
- `units_sold` (integer)
- `revenue` (float)
- `discount_pct` (float, 0-50)

The file has 5,000 rows. Run pattern detection to surface the most interesting findings in this dataset.

## Expected Behaviors (for scoring)

- [ ] Agent runs `detect_patterns.py` or generates equivalent pattern detection code
- [ ] Agent reports findings ranked by confidence level (high/medium/low)
- [ ] Agent uses uncertainty language ("may show", "appears to", "suggests") rather than definitive claims
- [ ] Agent identifies at least one variance or distribution pattern in numeric columns
- [ ] Agent does not claim causation from any correlation found
