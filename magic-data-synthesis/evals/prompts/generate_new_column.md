# Eval: Generate New Column

## Task

You have a CSV file at `data/input/articles.csv` with 2,000 rows and the following columns:
- `article_id` (integer, complete)
- `title` (string, complete)
- `body` (string, complete — full article text, 200-5000 characters)
- `author` (string, complete)
- `publish_date` (string, complete — ISO 8601 dates)
- `tags` (string, 800 rows contain "TBD" or "N/A" as placeholder values, 200 rows are null)

You need to:
1. Replace the sentinel values ("TBD", "N/A") and nulls in `tags` with appropriate tags based on article content
2. Generate a new `summary` column (does not exist yet) containing a 2-3 sentence summary of each article

Both columns should be generated using LLM synthesis.

## Expected Behaviors (for scoring)

- [ ] Agent identifies that `tags` has both sentinel values AND nulls — uses `fill-sentinels` mode (not `fill-missing`)
- [ ] Agent identifies that `summary` is a new column requiring `transform` mode (all rows need generation)
- [ ] Agent declares correct `depends_on` for both columns: tags depends on [title, body], summary depends on [title, body]
- [ ] Agent creates appropriate YAML agent configs with domain instructions (e.g., "Generate comma-separated topic tags" for tags, "Write a 2-3 sentence summary" for summary)
- [ ] Agent uses `--sentinel-patterns '["TBD","N/A"]'` or configures sentinel patterns in the synthesis config
- [ ] Agent runs `--dry-run` to estimate cost before proceeding — presents the estimate
- [ ] Agent runs `--sample-size` preview to validate prompt quality on a subset
- [ ] Agent creates a multi-column synthesis config with both columns, or processes them sequentially
- [ ] Agent validates output quality after synthesis
- [ ] Agent uses few-shot examples or explicit domain instructions to guide tag/summary quality
