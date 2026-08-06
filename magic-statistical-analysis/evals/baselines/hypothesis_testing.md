# Baseline: Hypothesis Testing

## Minimum Acceptable Behavior

An agent WITHOUT the statistical-analysis skill would typically:
- Run a t-test directly without checking normality first
- Report only the p-value ("p = 0.03, significant")
- Not compute or report effect size
- Not consider that time-on-page data is likely right-skewed
- Not warn about large-sample inflation of statistical significance

## With-Skill Expected Improvements

An agent WITH the statistical-analysis skill should:
1. **Normality check first** — run Shapiro-Wilk on each group before selecting the test; time-on-page data is typically right-skewed, so the agent should likely select Mann-Whitney U
2. **Effect size alongside p-value** — report Cohen's d (if t-test) or rank-biserial r (if Mann-Whitney U) with interpretation of magnitude (negligible/small/medium/large)
3. **Large-sample awareness** — note that with n=5,000, even trivially small differences (d < 0.1) can produce significant p-values; the effect size is the more informative measure
4. **Uncertainty language** — use "suggests", "appears to", "may indicate" rather than definitive claims
5. **Caveats** — include assumptions about independence and random sampling; note that statistical significance does not imply practical importance

## Key Differentiators

The skill prevents the most common statistical mistake: reporting p < 0.05 as "significant" without context. Without the skill, an agent might report "Variant B significantly increases time on page (p = 0.02)" when the actual effect is Cohen's d = 0.05 (negligible). With the skill, the agent reports both the p-value and the effect size, and correctly identifies the result as statistically significant but practically negligible.
