# Eval: Multi-Source Merge

## Task

You have 3 directories of parquet files from different content sources:
- `data/source_a/` — news articles (schema: `id`, `title`, `content`, `date`, 5 shards)
- `data/source_b/` — wiki articles (schema: `article_id`, `title`, `body`, `publish_date`, 3 shards)
- `data/source_c/` — forum posts (schema: `post_id`, `subject`, `text`, `created_at`, 4 shards)

Load all three sources into a unified dataset with consistent column names: `article_id`, `title`, `content`, `date`, `source`. Sample 500 records with balanced representation from each source.

## Context

- Total data: ~45,000 records across 12 parquet shards
- Schemas differ across sources — column names and semantics overlap but don't match
- Some records may appear in multiple sources (same article syndicated to news and wiki)
- The `id`/`article_id`/`post_id` columns serve the same purpose across sources

## Expected Behaviors (for scoring)

- [ ] Agent normalizes schemas across sources (maps `id`→`article_id`, `body`→`content`, `subject`→`title`, `text`→`content`, `publish_date`/`created_at`→`date`)
- [ ] Agent tracks source provenance per record (adds `source` field indicating which source directory each record came from)
- [ ] Agent deduplicates by normalized primary key (`article_id`) if same record appears in multiple sources
- [ ] Agent produces a balanced sample of 500 records across the 3 sources (not just first 500)
- [ ] Agent validates the merged dataset (total row count, null check across normalized columns, source distribution)
- [ ] Agent saves the unified dataset as a checkpoint with provenance metadata
