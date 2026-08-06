# Eval: Multi-Segment Analysis

## Task

You have a CSV file at `data/survey_responses.csv` with the following columns:
- `respondent_id` (integer)
- `age_group` (18-24, 25-34, 35-44, 45-54, 55+)
- `gender` (M, F, Other)
- `region` (Urban, Suburban, Rural)
- `satisfaction_score` (1-10 integer)
- `free_text_feedback` (text, 40% null)
- `product_used` (text)
- `recommendation_likelihood` (1-10 integer)

The file has 8,000 rows. Perform a comprehensive segment analysis to understand how satisfaction and recommendation likelihood vary across demographic groups. Identify any patterns that differ between aggregate and subgroup views.

## Expected Behaviors (for scoring)

- [ ] Agent runs `prepare_for_exploration.py` (or equivalent) to derive features from `free_text_feedback` and `product_used` text columns
- [ ] Agent runs segment analysis across multiple group columns (`age_group`, `gender`, `region`) — not just one
- [ ] Agent compares aggregate satisfaction patterns against per-segment patterns to check for Simpson's paradox
- [ ] Agent notes that `free_text_feedback` is 40% null and considers whether missingness correlates with satisfaction
- [ ] Agent presents findings ranked by confidence level with actionable next steps
- [ ] Agent does not report derived-column correlations (e.g., `feedback_length` vs `feedback_word_count`) as insights
