# Distribution Interpretation Guide

## Skewness

**Definition:** Measures asymmetry of the distribution around the mean.

| Skewness Value | Interpretation | Common in |
|---------------|----------------|-----------|
| -2 to -1 | Highly left-skewed | Age at retirement, test scores with ceiling |
| -1 to -0.5 | Moderately left-skewed | Customer satisfaction (most happy) |
| -0.5 to 0.5 | Approximately symmetric | Height, weight, well-designed measurements |
| 0.5 to 1 | Moderately right-skewed | Housing prices in affordable areas |
| 1 to 2 | Highly right-skewed | Income, wealth, city populations |
| >2 | Extremely right-skewed | Insurance claims, viral content views |

**Practical implications:**
- Right-skewed → median is more representative than mean
- Left-skewed → mean may underestimate typical values
- High skew → standard deviation is misleading, use IQR instead

## Kurtosis

**Definition:** Measures tailedness (not peakedness) of the distribution.

| Kurtosis Value | Interpretation | Implications |
|---------------|----------------|--------------|
| <3 (platykurtic) | Light tails, fewer outliers | Safer for parametric tests |
| ~3 (mesokurtic) | Normal-like tails | Standard statistical methods apply |
| >3 (leptokurtic) | Heavy tails, more outliers | Use robust methods, check for outliers |
| >7 | Very heavy tails | Strongly consider non-parametric methods |

## Normality Tests

### Shapiro-Wilk Test
- **Best for:** n < 5000 (most accurate for small-medium samples)
- **H0:** Data is normally distributed
- **p > 0.05:** Fail to reject normality (not proof of normality!)
- **p < 0.05:** Evidence against normality

**Caveats:**
- Very sensitive with large samples — almost always rejects for n > 5000
- Small p doesn't mean "very non-normal" — it means "enough evidence to detect departure"
- Visual inspection (Q-Q plot, histogram) is essential alongside the test

### Decision Tree: Is My Data Normal?

```
1. Visual: Does histogram look bell-shaped?
   → No: Not normal, use non-parametric methods
   → Yes: Continue

2. Skewness: |skewness| < 1?
   → No: Meaningfully skewed, consider transformation or robust methods
   → Yes: Continue

3. Shapiro-Wilk: p > 0.05?
   → Yes: Reasonable to treat as approximately normal
   → No (but n > 5000): May still be approximately normal — check visual + skewness
   → No (and n < 5000): Evidence against normality
```

## Common Distribution Shapes and What They Mean

### Right-Skewed (Log-Normal)
**Shape:** Long tail to the right
**Common in:** Income, prices, file sizes, response times
**Recommendation:** Report median, use log-transform for analysis, or use non-parametric tests

### Bimodal
**Shape:** Two distinct peaks
**Common in:** Mixed populations (male/female height), two-process data
**Recommendation:** Investigate subgroups, consider splitting analysis by group

### Uniform
**Shape:** Flat, roughly equal frequency across range
**Common in:** Random IDs, simulated data, uniformly sampled data
**Recommendation:** Check if this is expected — uniform numeric data may indicate synthetic/simulated data

### Zero-Inflated
**Shape:** Large spike at zero, then distribution for non-zero values
**Common in:** Insurance claims, rainfall, purchase amounts (many non-buyers)
**Recommendation:** Consider zero-inflated models, or analyze zeros separately from non-zeros

## When Results Are Unexpected

1. **Everything looks normal but shouldn't:** Check for data aggregation (Central Limit Theorem) or small sample size
2. **Extreme skewness (>5):** Check for data entry errors, unit mismatches, or multiplicative processes
3. **Bimodal when not expected:** Look for a hidden grouping variable (gender, region, product type)
4. **All columns normal:** Suspiciously clean — verify data source, check for synthetic data
