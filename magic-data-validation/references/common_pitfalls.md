# Common Statistical Pitfalls Reference

## 1. Join Explosion

**What:** Merging two tables produces far more rows than either input because of many-to-many key matches.

**Detection:** `rows_out > 2 * max(rows_left, rows_right)`

**Example:** Joining customers (1000 rows) with orders (5000 rows) on `product_category` — if 50 customers share a category with 100 orders each, you get 5000 rows from that category alone.

**Fix:** Check join key cardinality before merging. Use left join with deduplication, or aggregate one side first.

## 2. Survivorship Bias

**What:** Only analyzing data that "survived" a selection process, missing the dropped/filtered cases.

**Detection:**
- Check if data has suspicious gaps in expected ranges
- Look for filter columns where one value dominates (>90%)
- Check if temporal data has sudden drops (people/items removed)

**Example:** Analyzing only successful companies to find success patterns — fails because unsuccessful companies aren't in the data.

**Fix:** Document what data is missing. Note the selection process. Report survivorship risk in caveats.

## 3. Simpson's Paradox

**What:** A trend that appears in aggregated data reverses when the data is split by a confounding variable.

**Detection:**
- Compute correlation/trend for full dataset
- Re-compute per subgroup (by each categorical variable)
- Check if any subgroup shows opposite direction

**Example:** Overall, drug B has higher recovery rate. But within each severity group, drug A is better — drug B was given to less severe cases.

**Fix:** Always check trends within relevant subgroups. Report if reversal is detected.

## 4. Look-Ahead Bias

**What:** Using information that wouldn't have been available at the time of the analysis in a predictive context.

**Detection:**
- Check datetime columns for future dates relative to other timestamps
- Look for columns that could only be known after the outcome (e.g., "days_to_resolution" when predicting if issue will be resolved)

**Example:** Using "final sale price" as a feature to predict "will the item sell" — the final price is only known after the sale.

**Fix:** Identify the "prediction point" in time. Remove all features that aren't available at that point.

## 5. Selection Bias

**What:** The data doesn't represent the population of interest due to non-random sampling.

**Detection:**
- Check if distributions match expected population distributions
- Look for suspicious gaps or truncation (e.g., all ages > 18)
- Check if temporal coverage is complete

**Example:** Survey data from online respondents — misses people without internet access.

**Fix:** Document the sampling method. Report likely biases. Weight data if population distributions are known.

## 6. Metric Gaming

**What:** Data shows suspicious patterns suggesting the metric was optimized rather than the underlying behavior.

**Detection:**
- Check for round-number concentrations (many values at exactly 100, 50, 0)
- Check for values clustered just above/below thresholds
- Check for end-of-period spikes

**Example:** Sales data shows 40% of transactions at exactly $99.99 or $49.99 — pricing thresholds, not natural distribution.

**Fix:** Note the pattern. Consider whether the metric is appropriate. Report in caveats.

## 7. Ecological Fallacy

**What:** Drawing individual-level conclusions from group-level (aggregated) data.

**Detection:**
- Check if data appears to be pre-aggregated (all numeric, low row count, "count" or "total" columns)
- Check for suspiciously smooth distributions (no noise)

**Example:** States with higher average income have lower crime rates — doesn't mean wealthy individuals commit fewer crimes.

**Fix:** Analyze at the appropriate level. Don't attribute group trends to individuals. Report aggregation level in methodology.

## Magnitude Checks

| Check | Trigger | Severity |
|-------|---------|----------|
| Max >> Median | max > 1000 × median | High — likely data error or outlier |
| Negative where unexpected | min < 0 for price, count, age | Medium — data entry error |
| Zero where unexpected | Many zeros in revenue, score | Medium — check if zeros are real or missing |
| Future dates | Date > today + 1 year | High — likely data error |
| Impossible values | Age > 150, temperature > 200°F for weather | High — data validation needed |
