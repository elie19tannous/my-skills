# Statistical Interpretation Guide

## Uncertainty Language (Mandatory)

### Use These Phrases
- "The data suggests..."
- "This appears to indicate..."
- "There may be a relationship between..."
- "The analysis indicates a possible..."
- "Results are consistent with..."
- "The evidence points toward..."

### Never Use These Phrases
- "This proves..."
- "Definitively shows..."
- "Always/never..."
- "Causes/caused by..." (unless experimental design)
- "Is significant" (without effect size context)

## Interpreting p-values

**What p-value IS:** The probability of observing data this extreme if the null hypothesis were true.

**What p-value IS NOT:** The probability that the hypothesis is true/false.

| p-value | Interpretation |
|---------|---------------|
| < 0.001 | Very strong evidence against H0 |
| 0.001 - 0.01 | Strong evidence against H0 |
| 0.01 - 0.05 | Evidence against H0 |
| 0.05 - 0.10 | Weak evidence against H0 |
| > 0.10 | Insufficient evidence against H0 |

**Always pair with effect size:** A small p-value with a tiny effect size means the effect is statistically detectable but practically meaningless.

## Writing Statistical Narratives

### Template for Group Comparison
"The [value_col] appears to differ between [group_a] (median = X, n = N) and [group_b] (median = Y, n = N). A [test_name] suggests this difference [is/is not] statistically significant (p = P, [effect_size_name] = E, [interpretation]). However, [caveat about sample size/assumptions/confounders]."

### Template for Correlation
"There appears to be a [strength] [positive/negative] [method] correlation between [col_a] and [col_b] (r = R, p = P). This suggests that as [col_a] increases, [col_b] tends to [increase/decrease]. Note: correlation does not imply causation — [possible confounders]."

### Template for Distribution
"The distribution of [col] appears [shape] (skewness = S, kurtosis = K). The median (M) [is close to / differs substantially from] the mean (X), suggesting [symmetric data / presence of outliers or skew]. A Shapiro-Wilk test [supports / does not support] the assumption of normality (p = P)."

## Mandatory Caveats

Every statistical output MUST include at least one caveat. Common caveats:

1. "Sample size (n = N) may limit statistical power"
2. "Correlation does not imply causation"
3. "Results may not generalize beyond this dataset"
4. "Multiple comparisons increase the risk of false positives"
5. "Outliers may influence these results"
6. "Non-normal distribution may affect parametric test accuracy"
7. "Missing data (X%) may introduce bias"
8. "Analysis limited to the provided dataset"
