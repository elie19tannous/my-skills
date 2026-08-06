# Baseline: Multi-Table Merge

## Minimum Acceptable Behavior

An agent reading the transformation SKILL.md should:

1. **Check join key types**: Verify `product_id` is the same type in both files before merging. The SKILL.md constraint says "MUST cast join keys to the same type before merging." In this case both are strings, so no cast is needed — but the agent should explicitly confirm this.

2. **Check cardinality**: Verify `product_id` is unique in `products.csv` (the right table). The SKILL.md rule says "Before merging, check `df[key].duplicated().sum()` on both sides." With a unique right key and a left join, there is no explosion risk.

3. **Use left join**: Preserve all 5000 orders. The agent should choose left join because we want every order in the output, even if a product is missing from the products table.

4. **Verify post-merge row count**: With a unique right key and a left join, `rows_out` must equal `rows_left` (5000). If it does not, something went wrong.

5. **Derive total_price after merge**: Calculate `quantity * unit_price` only after both columns are available from the merge. This follows the transformation ordering rule: join first, then derive.

6. **Validate output**: Check for unexpected nulls in product columns (product_name, category, unit_price) — these indicate unmatched orders. Report how many orders had no matching product.

## Code Quality Indicators

- Explicit cardinality check before merge (`products['product_id'].duplicated().sum()`)
- Uses `pd.merge()` with `how='left'`
- Derives `total_price` using vectorized multiplication, not `apply()`
- Checks `rows_out == rows_left` after merge
- Reports null counts in joined columns

## Anti-patterns to Flag

- Merging without checking key types or cardinality
- Using inner join (loses orders without matching products)
- Deriving total_price before the merge (column not yet available)
- Not checking for join explosion
- Using `iterrows()` for the calculation
