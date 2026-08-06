# Baseline: Large Dataset Profiling

## Minimum Acceptable Behavior

A correctly guided agent should:

1. **Sample before full profiling**:
   - Use `--sample-size 10000` or equivalent sampling in generated code
   - Explicitly state that initial results are based on a sample
   - Note the uncertainty: "sampled results may miss rare patterns present in the full 5M rows"

2. **Avoid dangerous operations**:
   - NOT run `detect_all_issues.py` on 5M rows without `--sample-size`
   - NOT attempt a 25-column correlation heatmap at full scale (would OOM)
   - NOT try to run TF-IDF/KMeans on 5M text rows without sampling

3. **Profile strategically after sample review**:
   - Review sample profiling results first
   - Identify columns that need full-scale analysis (e.g., `amount` for outlier detection in fraud context)
   - Run targeted scripts on specific columns at full scale
   - Use `--columns` to limit correlation analysis scope

4. **Use caching for expensive operations**:
   - Implement or reference the `cached_or_compute` pattern
   - Cache quality scores, distribution results, correlation matrices
   - Avoid recomputing when re-running after adjustments

5. **Report with appropriate context**:
   - "5M rows, 25 columns, profiled via 10K sample + targeted full-scale analysis"
   - Note that fraud detection requires special attention to outliers in `amount` and category balance in `currency`/`merchant_category`
   - Profile `description` with text metrics (length distribution, vocabulary), not numeric stats

## Failure Modes

- Runs comprehensive profiling on full 5M rows (OOM or 30+ minute timeout)
- Does not mention sampling or uncertainty in results
- Treats all 25 columns identically instead of targeting key columns
- Applies numeric profiling to the `description` text column
- Does not consider the fraud detection use case when interpreting results
- Computes 25x25 correlation matrix at full scale
