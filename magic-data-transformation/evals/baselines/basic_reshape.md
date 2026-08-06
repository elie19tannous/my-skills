# Baseline: Basic Reshape

## Minimum Acceptable Behavior

An agent reading the transformation SKILL.md should:

1. **Identify the operation**: Recognize this as a melt (unpivot) operation — converting wide format to long format.

2. **Specify correct parameters**:
   - `id_vars`: `['salesperson', 'region']` (columns to keep as identifiers)
   - `value_vars`: `['q1_sales', 'q2_sales', 'q3_sales', 'q4_sales']` (columns to melt)
   - `var_name`: `'quarter'` (meaningful name, not default `'variable'`)
   - `value_name`: `'sales'` (meaningful name, not default `'value'`)

3. **Track row count change**: The agent should note that 3 rows with 4 value columns produces 12 output rows (3 * 4 = 12). This matches the SKILL.md rule: "Melt multiplies rows by the number of value columns."

4. **Validate output**: Check that output shape is (12, 4) — 12 rows, 4 columns (salesperson, region, quarter, sales).

## Code Quality Indicators

- Uses `pd.melt()` directly, not a manual loop
- Names output columns meaningfully (not `variable`/`value`)
- Includes a shape assertion or row count check
- Does not attempt to "fix" any structural NaNs (there should be none in this case since all cells have values)

## Anti-patterns to Flag

- Using `iterrows()` or manual reshape logic
- Not tracking row count change
- Leaving default column names (`variable`, `value`)
- Pivoting when melt is the correct operation
