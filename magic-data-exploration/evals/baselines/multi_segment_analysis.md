# Baseline: Multi-Segment Analysis

## Expected Agent Behavior

### Minimum Requirements

1. **Prepares text columns**: Agent runs `prepare_for_exploration.py` or equivalent to derive numeric features from `free_text_feedback` (length, word count, presence) and `product_used` (length, presence) before running exploration scripts.

2. **Analyzes multiple segment dimensions**: Agent runs segment analysis across at least two of the three demographic group columns (`age_group`, `gender`, `region`), not just one. Comprehensive analysis examines all three.

3. **Checks for Simpson's paradox**: Agent compares aggregate satisfaction/recommendation patterns against per-segment breakdowns. For example, overall satisfaction might appear flat across regions, but within each age group, Urban satisfaction could be consistently higher — masked by demographic composition differences.

4. **Addresses null pattern in feedback**: Agent notes that `free_text_feedback` is 40% null and investigates whether missingness correlates with `satisfaction_score` or `recommendation_likelihood`. Respondents who leave feedback may be systematically different (more satisfied or more dissatisfied) from those who don't.

5. **Presents ranked findings**: Findings are ordered by confidence level (high first) with actionable next steps for each. The agent does not bury the most important finding in a list of trivial observations.

6. **Excludes trivial correlations**: Agent does not report `feedback_length` vs `feedback_word_count` as an insight, since both are derived from the same text column.

### Quality Indicators

- Agent considers interaction effects (e.g., does the gender gap in satisfaction differ across age groups?)
- Agent notes group size imbalances that may affect reliability of comparisons
- Agent suggests which segments warrant targeted follow-up (surveys, interviews, product changes)
- Agent considers whether the 5-tier age grouping might mask patterns (e.g., 18-24 and 55+ might both be dissatisfied but for different reasons)
- Agent proposes a transition to action: "Based on these findings, the next step might be cleaning the feedback text for synthesis, or running formal hypothesis tests via magic-statistical-analysis"
