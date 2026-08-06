# Baseline: Complex Transformation Pipeline

## Minimum Acceptable Behavior

An agent reading the transformation SKILL.md should:

1. **Cast types before joining**: The SKILL.md constraint says "MUST cast join keys to the same type before merging." `store_id` is int in transactions but string in stores. The agent must cast one to match the other before the first join.

2. **Check cardinality on both joins**:
   - `store_id`: should be unique in stores (50 unique values). Check `stores['store_id'].duplicated().sum() == 0`.
   - `product_id`: should be unique in products (500 unique values). Check `products['product_id'].duplicated().sum() == 0`.
   - Both are one-to-many (unique right, duplicated left), so no explosion risk — but the agent should verify.

3. **Follow transformation ordering**: The SKILL.md rule prescribes: type cast -> join -> filter -> derive -> aggregate -> reshape. The agent should:
   - Cast `store_id` types (step 1)
   - Join transactions + stores, then join + products (step 2)
   - Filter to Q1 2025 (step 3)
   - Derive `profit` and `margin_tier` (step 4)
   - Aggregate by region + category (step 5)
   - Pivot to final shape (step 6)

4. **Use np.where for margin_tier**: The SKILL.md seed pattern shows `np.where` chains for multi-branch conditional logic. The agent should produce:
   ```python
   margin = profit / amount
   df['margin_tier'] = np.where(margin > 0.5, 'high',
                       np.where(margin > 0.2, 'medium', 'low'))
   ```

5. **Aggregate at correct grain**: Group by `['region', 'category']`. Verify the output row count equals the number of unique (region, category) pairs. Sum `amount` for revenue, sum `profit`, count `txn_id` for transaction count.

6. **Handle pivot prerequisites**: Before pivoting, ensure no duplicate (region, category) pairs exist in the aggregated data (they should not after a proper group-by, but the agent should be aware of the constraint).

7. **Save checkpoints**: At least one intermediate file (after joins, after filtering, or after derivation) for debugging and resume.

8. **Validate final output**: Check shape, verify no unexpected nulls, confirm row count matches expected number of regions.

## Code Quality Indicators

- Explicit type casting before joins
- Cardinality checks before both merges
- Correct transformation ordering (not filtering before joining, not deriving before all data is available)
- `np.where` chain for conditional column, not `apply()` with lambda
- Vectorized aggregation via `groupby().agg()`, not manual loops
- At least one checkpoint saved
- Post-pipeline validation with shape and null checks

## Anti-patterns to Flag

- Joining without type casting (produces all-NaN join or empty result)
- Skipping cardinality check
- Filtering before joining (loses ability to join on filtered-out rows)
- Deriving profit before the products join (cost column not yet available)
- Using `apply()` with lambda for margin_tier
- Pivoting without verifying unique (index, columns) pairs
- No intermediate checkpoints
- No final validation
