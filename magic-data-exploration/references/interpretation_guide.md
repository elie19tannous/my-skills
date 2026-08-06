# Exploration Interpretation Guide

## Writing Finding Descriptions

### Confidence Levels

| Level | Criteria | Language |
|-------|----------|----------|
| High | p < 0.01, or >90% pattern match | "The data clearly shows...", "There is strong evidence..." |
| Medium | p < 0.05, or >70% match | "The data suggests...", "There appears to be..." |
| Low | Suggestive but not conclusive | "There may be...", "It's possible that..." |

### Finding Templates

**Pattern Discovery:**
> "[confidence] [description of pattern] was detected in [column(s)]. [evidence with numbers]. [implication or follow-up suggestion]."

**Example:**
> "There appears to be a strong positive correlation (r=0.82, p<0.001) between marketing_spend and revenue. This suggests that as marketing investment increases, revenue tends to increase as well. However, correlation does not imply causation — other factors may drive both variables."

**Segment Analysis:**
> "[group_a] (n=N, median=M) appears to differ from [group_b] (n=N, median=M) on [variable]. A [test] suggests this difference [is/is not] statistically significant (p=P). [effect size and interpretation]."

## Discover-Then-Act Pattern

1. **First:** Run detect_patterns.py — let the data tell you what's interesting
2. **Then:** Investigate the top findings with targeted analysis
3. **Never:** Start with a hypothesis and look only for confirming evidence

## What Counts as "Interesting"

| Finding | Interesting If |
|---------|---------------|
| Correlation | |r| > 0.5 AND p < 0.05 |
| Categorical imbalance | One value > 80% |
| Outlier cluster | >5% of rows are outliers |
| Temporal pattern | Consistent cycle across >3 periods |
| Missing pattern | Missingness correlates with another column |
| Simpson's paradox | Trend reverses in subgroups |

## Caveats for Exploration

Always include:
1. "Findings are exploratory and should be confirmed with targeted analysis"
2. "Multiple patterns were examined, increasing false discovery risk"
3. "Correlation does not imply causation" (for any relationship finding)
