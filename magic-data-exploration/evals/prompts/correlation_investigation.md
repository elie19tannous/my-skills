# Eval: Correlation Investigation

## Task

You have a CSV file at `data/text_corpus.csv` with the following columns:
- `id` (integer)
- `title` (text)
- `body` (text)
- `category` (news, opinion, review, tutorial)
- `author` (text)
- `publish_date` (YYYY-MM-DD)
- `word_count` (integer — pre-computed)

The file has 12,000 rows. A colleague says "longer titles correlate with longer articles." Investigate whether this claim holds, and whether there are other interesting relationships in the data.

## Expected Behaviors (for scoring)

- [ ] Agent prepares text columns for exploration (derives `title_length`, `body_length`, etc.) or uses `prepare_for_exploration.py`
- [ ] Agent checks the title-length vs body-length correlation but recognizes it may be a derived-column artifact if both come from text features
- [ ] Agent filters out trivially correlated derived columns (e.g., `body_length` vs `body_word_count`) before reporting insights
- [ ] Agent checks whether the title-body correlation holds across categories (subgroup check / Simpson's paradox awareness)
- [ ] Agent uses hedged language distinguishing correlation from causation
- [ ] Agent reports confidence levels for findings
