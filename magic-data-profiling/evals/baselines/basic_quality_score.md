# Baseline: Basic Quality Score

## Minimum Acceptable Behavior

A correctly guided agent should:

1. **Detect column types** before applying profiling methods:
   - `id`: numeric (integer)
   - `name`, `email`: text/string
   - `age`: numeric (integer, with nulls)
   - `signup_date`: text/string (inconsistent date formats)
   - `status`: text/string (low cardinality, categorical)

2. **Compute quality dimensions** separately:
   - **Completeness**: ~92% (8% missing in `age` and `email`). Score should be around 84/100 based on linear scaling (100 - 8*2).
   - **Consistency**: Should flag mixed casing in `status` and mixed date formats in `signup_date`. At least 2 consistency issues.
   - **Uniqueness**: Should check for duplicate rows. With unique `id`, duplicates should be near 0.
   - **Validity**: Should check for outliers in `age` (any values <0 or >120?).

3. **Report per-column breakdown**: Not just "overall: 85/100" but show each dimension score and which columns contributed to each.

4. **Include context**: "5,000 rows, 6 columns. For production model input, the inconsistent date formats in `signup_date` and mixed casing in `status` should be normalized before downstream use."

## Failure Modes

- Reports only the aggregate score without per-column breakdown
- Does not detect the mixed date formats as a consistency issue
- Does not detect the mixed casing as a consistency issue
- Uses LLM to "estimate" the quality score instead of computing it
- Reports score without row/column count context
