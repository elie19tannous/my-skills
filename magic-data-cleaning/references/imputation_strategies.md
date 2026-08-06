# Imputation Strategies Reference

## Decision Tree: Choosing an Imputation Strategy

```
Is column missing >50%?
├─ Yes → DROP the column (unreliable for analysis)
└─ No → What is the column type?
    ├─ Numeric
    │   ├─ Is distribution normal? → MEAN imputation
    │   ├─ Is distribution skewed? → MEDIAN imputation
    │   ├─ Is dataset small (<100K rows)? → KNN imputation (k=5)
    │   └─ Is dataset large (>=100K rows)? → MEDIAN imputation
    ├─ Categorical
    │   ├─ Is there a dominant category (>70%)? → MODE imputation
    │   └─ Is distribution balanced? → MODE or "Unknown" category
    ├─ Text
    │   ├─ Is field required? → Flag as "MISSING"
    │   └─ Is field optional? → Empty string
    └─ DateTime
        └─ Forward-fill or interpolate if time series
```

## Strategy Details

### Mean Imputation
- **When:** Normal distribution, <10% missing
- **Pro:** Preserves mean
- **Con:** Reduces variance, distorts relationships
- **Use:** Quick analysis, small missing %

### Median Imputation
- **When:** Skewed distribution, any % missing
- **Pro:** Robust to outliers
- **Con:** May create artificial spike at median
- **Use:** Default for numeric data

### KNN Imputation
- **When:** Small-medium dataset (<100K), complex relationships between columns
- **Pro:** Uses multivariate relationships, adapts to local patterns
- **Con:** Slow on large data, sensitive to scale
- **Use:** When accuracy matters and dataset fits in memory

### Mode Imputation (Categorical)
- **When:** Categorical data with a clear dominant value
- **Pro:** Simple, preserves most common value
- **Con:** Amplifies existing imbalance
- **Use:** Default for categorical data

### Drop Rows
- **When:** <5% of rows affected, or analysis requires complete cases
- **Pro:** No artificial data introduced
- **Con:** Reduces sample size, may introduce bias if missingness is not random
- **Use:** When complete cases are sufficient

### Drop Column
- **When:** >50% missing, column not critical for analysis
- **Pro:** Removes unreliable data entirely
- **Con:** Loses potentially useful information
- **Use:** Very high missing %, or column is redundant

## Text-Specific Missing Value Handling

| Strategy | When | What it does |
|----------|------|-------------|
| Empty string | Optional field | Replace NaN with "" |
| "MISSING" flag | Required field | Replace NaN with "MISSING" for tracking |
| Drop row | Critical field | Remove row if text is essential |
| Forward fill | Sequential text (logs) | Fill with previous entry |

## Common Pitfalls

1. **Imputing before splitting train/test:** Causes data leakage — impute after splitting
2. **Using mean on skewed data:** Distorts the distribution — use median instead
3. **Ignoring missing patterns:** Missing values may be informative (e.g., income missing = unemployed)
4. **Imputing too aggressively:** Creating artificial data that doesn't reflect reality
5. **Not tracking what was imputed:** Always report which columns were imputed and how
