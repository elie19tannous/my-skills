# Eval: Hypothesis Testing

## Task

You have a CSV file at `data/ab_test_results.csv` containing results from an A/B test on a website. The file has 5,000 rows and columns: user_id, variant (A or B), time_on_page_seconds, converted (0 or 1), pages_viewed. Compare time_on_page_seconds between variant A and variant B. Determine whether the difference is statistically significant and report the practical significance.

## Context

- This is a two-group comparison (variant A vs variant B)
- The value column (time_on_page_seconds) is continuous and may or may not be normally distributed
- Time-on-page data is often right-skewed (many short visits, few very long ones)
- The sample size is large (5,000), so even trivial differences may be statistically significant
- You need to report both statistical and practical significance

## Expected Behaviors (for scoring)

- [ ] Agent checks normality of time_on_page_seconds in each group (Shapiro-Wilk) before choosing test
- [ ] Agent selects appropriate test (t-test if normal, Mann-Whitney U if not)
- [ ] Agent reports p-value AND effect size (Cohen's d or rank-biserial r)
- [ ] Agent interprets effect size magnitude (negligible/small/medium/large)
- [ ] Agent uses uncertainty language ("suggests", "appears to", "may indicate")
- [ ] Agent notes that large sample sizes can produce significant p-values for trivially small effects
- [ ] Agent includes caveats about assumptions (independence, random sampling)
