# Data Profiling Guide

## Profiling Workflow

1. **Start with basic_stats.py** — get column types, counts, basic statistics
2. **Check for missing values** — run null_analysis.py
3. **Analyze distributions** — run distribution_analysis.py for skewness, normality
4. **Check correlations** — run correlation_matrix.py for relationships
5. **Detect outliers** — run outlier_detection.py for anomalies
6. **Assess quality** — run quality_score.py for composite score

## Interpreting Profiling Results

### Missing Values

| Missing % | Severity | Action |
|-----------|----------|--------|
| 0-1% | Low | Safe to impute with median/mode |
| 1-5% | Low-Medium | Impute, investigate pattern |
| 5-20% | Medium | Investigate cause, consider multiple imputation |
| 20-50% | High | Column may be unreliable, consider dropping |
| >50% | Critical | Likely drop column, or investigate data source |

### Distribution Shapes

| Shape | Skewness | Kurtosis | Typical Data |
|-------|----------|----------|-------------|
| Normal | ~0 | ~3 | Height, test scores, measurement errors |
| Right-skewed | >0.5 | Varies | Income, prices, file sizes, population |
| Left-skewed | <-0.5 | Varies | Age at retirement, late arrival times |
| Heavy-tailed | ~0 | >3 | Financial returns, earthquake magnitudes |
| Light-tailed | ~0 | <3 | Uniform-like data, bounded measurements |
| Bimodal | ~0 | <3 | Mixed populations, two-process data |

### When to Use Which Profiling Script

| Question | Script | Key Output |
|----------|--------|------------|
| What's in this data? | basic_stats.py | Column types, counts, ranges |
| How much is missing? | null_analysis.py | Missing counts, patterns |
| What shape are distributions? | distribution_analysis.py | Skewness, normality |
| Are columns related? | correlation_matrix.py | Correlations, significance |
| Are there outliers? | outlier_detection.py | Outlier counts, bounds |
| How good is this data? | quality_score.py | Score 0-100, grade A-F |

## Text Column Profiling

When a column is detected as text (mean length > 20 or high cardinality):

**Report instead of numeric stats:**
- Character length: min, max, mean, median
- Word count: min, max, mean, median
- Vocabulary size (unique terms)
- Top 20 most frequent terms
- Empty string count

**Red flags in text data:**
- Very high vocabulary size (near row count) — possibly unique identifiers
- Very low vocabulary size — possibly categorical, not text
- Many empty strings — missing values disguised
- Extreme length outliers — possible data entry errors
