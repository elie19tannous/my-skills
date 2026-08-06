# Exploration Heuristics Reference

Data-shape-specific guidance for choosing exploration strategies and scripts.

## Data-Shape-Specific Heuristics

| Data Shape | Key Questions | Recommended Approach |
|---|---|---|
| Time-series | Is there seasonality? Trend direction? Breakpoints or regime changes? Gap frequency? | Run `detect_patterns.py` with time-column specified. Look for autocorrelation and stationarity. Plot rolling averages at multiple windows (7, 30, 90) before concluding trend direction. |
| Text-heavy | What is the distribution of text lengths? Are there repeated phrases or templates? Language mix? | Use `segment_analysis.py` to cluster by text length and token frequency. Extract top n-grams before deeper NLP. Check for boilerplate or auto-generated content that skews analysis. |
| High-cardinality categorical (>100 unique) | Are there dominant categories? Long tail? Misspellings or near-duplicates? | Run `segment_analysis.py` to identify the top 20 categories by frequency. Collapse the tail into "Other". Use fuzzy matching to detect near-duplicate labels before grouping. |
| Mostly numeric | Are distributions normal, skewed, or multimodal? Outlier prevalence? Correlation structure? | Run `relationship_explorer.py` for pairwise correlations. Use `detect_patterns.py` for outlier detection. Check for log-normal distributions before computing means -- medians may be more appropriate. |
| Mixed types (numeric + categorical + dates) | Which columns are truly independent? Are types correctly inferred? Hidden encodings? | Run `prepare_for_exploration.py` first to validate type inference. Then `relationship_explorer.py` on numeric subset and `segment_analysis.py` on categorical subset separately before cross-analysis. |
| Sparse data (>50% null) | Is missingness random or systematic? Which columns are usable? Are nulls informative? | Run `detect_patterns.py` with null-analysis mode. Map null co-occurrence across columns. Do NOT drop sparse columns before checking if nullness itself is a signal (e.g., "field is null only for free-tier users"). |

## Script Selection Quick Reference

Use this to pick the right starting script based on what you observe after initial profiling:

- **`prepare_for_exploration.py`**: Always run first when data has mixed or ambiguous types.
  Handles type coercion, date parsing, and basic cleaning to make other scripts reliable.
- **`detect_patterns.py`**: Use when looking for trends, anomalies, periodicity, or structural
  breaks. Best for time-series and numeric data. Also handles null-pattern analysis.
- **`segment_analysis.py`**: Use when the goal is to find meaningful groups, clusters, or
  segments. Best for categorical and text data. Also useful for identifying subpopulations
  in numeric data.
- **`relationship_explorer.py`**: Use when the goal is understanding how columns relate to
  each other. Computes correlations, cross-tabs, and conditional distributions. Best after
  initial profiling narrows the column set.

### Typical Script Sequences

- **First exploration of unknown data**:
  `prepare_for_exploration.py` -> `detect_patterns.py` -> `relationship_explorer.py`
- **Segmentation-focused analysis**:
  `prepare_for_exploration.py` -> `segment_analysis.py` -> `relationship_explorer.py` (within segments)
- **Time-series deep dive**:
  `prepare_for_exploration.py` -> `detect_patterns.py` (with time column) -> `segment_analysis.py` (for regime detection)
- **Sparse data investigation**:
  `prepare_for_exploration.py` -> `detect_patterns.py` (null analysis) -> `segment_analysis.py` (group by missingness)

## Warning Signs: Patterns That Look Real But Aren't

Watch for these during exploration -- they produce convincing but spurious findings:

- **Simpson's paradox**: A trend that appears in aggregated data but reverses when split
  by a confounder. Always check findings across key subgroups before reporting.
- **Survivorship bias**: If the dataset only contains "successful" records (active users,
  completed transactions), patterns may not generalize. Ask what is missing from the data.
- **Binning artifacts**: Histograms and grouped summaries are sensitive to bin boundaries.
  If a pattern only appears at one bin width, it is likely an artifact.
  Test with 2-3 different bin sizes.
- **Calendar effects masking trends**: Day-of-week and month-end effects can dominate short
  time windows. Deseasonalize before claiming a trend over periods shorter than one full cycle.
- **Correlation from shared denominators**: Two rates that share a denominator (e.g., revenue
  per user and cost per user) will be mechanically correlated. Verify with absolute numbers.
- **Small-group amplification**: Segments with few observations produce extreme rates
  (e.g., "100% conversion" from 2 users). Apply minimum sample size thresholds
  before ranking segments.
- **Timestamp truncation artifacts**: When dates are truncated to month or week, events
  near boundaries get misattributed. Check raw timestamps before grouping by period.
