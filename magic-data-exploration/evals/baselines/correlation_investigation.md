# Baseline: Correlation Investigation

## Expected Agent Behavior

### Minimum Requirements

1. **Prepares text columns**: Agent derives numeric features from text columns (`title_length`, `body_length`, or similar) using `prepare_for_exploration.py` or equivalent code, since the raw text columns cannot be directly correlated.

2. **Filters derived-column correlations**: Agent recognizes that `body_length` vs `body_word_count` (both derived from `body`) will trivially correlate and excludes these from reported insights. The SKILL.md explicitly warns: "NEVER report derived-column correlations as insights."

3. **Checks subgroups for Simpson's paradox**: Agent checks whether the title-body length correlation holds when split by `category`. A correlation that exists in aggregate but vanishes or reverses within categories (news, opinion, review, tutorial) would be a Simpson's paradox case.

4. **Distinguishes correlation from causation**: Agent does not state that longer titles "cause" longer articles. Uses language like "associated with", "co-occurs with", or "correlates with".

5. **Reports confidence levels**: Each finding includes explicit confidence (high/medium/low) with justification based on sample size, statistical significance, and subgroup consistency.

### Quality Indicators

- Agent checks the pre-computed `word_count` column against derived `body_word_count` for consistency
- Agent explores whether `category` mediates the relationship (e.g., tutorials may have both longer titles and longer bodies, creating a spurious aggregate correlation)
- Agent suggests further investigation paths (e.g., time-based trends, author-specific patterns)
- Agent notes that the `publish_date` column could be used for temporal analysis
