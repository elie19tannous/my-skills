# Domain-Specific Validation Rules

## Financial Validation

- Verify balance checks: sum of debits must equal sum of credits within each transaction group. Flag imbalances >0.01
- Check currency consistency within a dataset — if multiple currencies exist, ensure a currency column is present and populated
- Validate percentage fields fall within 0-100 (or 0-1 depending on format). Flag negative percentages and values >100
- Validate that unit prices × quantities = line totals within rounding tolerance (abs difference ≤ 0.01)
- Check for suspicious round numbers in datasets that should have decimals — may indicate placeholder or default values
- Verify that financial dates fall within the expected reporting period — no transactions dated in the future or before entity creation

## Temporal Validation

- Validate chronological ordering: start_date must be < end_date. Flag rows where start > end
- Flag future dates when the data represents historical records — unless the dataset explicitly includes forecasts
- Check consistent granularity: if most timestamps are daily, flag any that are hourly or monthly as potential errors
- Detect gaps in time series: generate the expected date range and identify missing periods
- Validate that event sequences follow expected order (e.g., created → approved → shipped → delivered)
- Check for impossible dates: Feb 30, month 13, timestamps before Unix epoch (when using epoch integers)
- Validate that duration calculations are non-negative: if computed from end - start, negative durations indicate data errors

## Cross-Column Consistency

- When status="completed", validate that completed_date is NOT NULL. Flag completed records without completion dates
- When quantity=0, validate that total_price=0. Flag zero-quantity rows with non-zero totals
- When a parent record is inactive/deleted, validate that child records are also inactive/deleted
- Validate that calculated columns match their formula: if margin = (revenue - cost) / revenue, recompute and compare
- Check mutually exclusive flags: if is_domestic=True, then is_international must be False
- Validate that category assignments match allowed values — use a reference list, not just NULL checks

## Referential Integrity

- Verify that every foreign key value exists in the referenced primary key column. Report orphaned records
- Check for primary key uniqueness — duplicates in the primary key indicate data quality issues upstream
- When merging datasets, count rows before and after join. Unexpected row increases indicate duplicate keys
- Validate that lookup/dimension tables are complete — every code used in fact tables must have a corresponding dimension entry
- Check bidirectional integrity: if orders reference customers, verify no customer IDs exist only in orders but not in customers
- Validate composite keys: when uniqueness depends on multiple columns (e.g., date + product + region), check uniqueness of the combination

## Distribution Stability

- Compare new data distributions to historical baselines — flag columns where mean shifts by >2 standard deviations
- Monitor NULL rate changes: if a column historically has <1% NULLs and a new batch has 15%, flag it before processing
- Track cardinality changes: if a category column historically has 50 unique values and a new file has 200, investigate
- Compare row count to expected range: if daily loads are typically 10K-15K rows, flag a batch with 500 or 50K rows
- Check value range stability: min and max should stay within historical bounds unless a known change occurred
- Validate proportion stability: if a category historically represents 30% of rows, flag batches where it drops to 5% or jumps to 80%
- When distribution shifts are detected, classify as structural (expected change) or anomalous (data quality issue) before proceeding
- Validate data type consistency: if a column was historically integer, a batch with float values may indicate upstream changes
