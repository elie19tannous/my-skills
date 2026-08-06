# Baseline: Multi-Source Merge

## Minimum Acceptable Behavior

An agent WITHOUT the data-loading skill would typically:
- Load each source directory independently with `pd.read_parquet()`
- Try `pd.concat()` directly, resulting in misaligned columns (e.g., `content` from source_a alongside `body` from source_b as separate columns, with NaN fill)
- Not track which records came from which source
- Not handle deduplication across sources
- Not produce a balanced sample (would just take first 500 from concatenated result, biased toward source_a)

## With-Skill Expected Improvements

An agent WITH the data-loading skill should:
1. **Schema normalization** — map equivalent columns across sources before merging, producing a clean unified schema
2. **Source provenance** — add a `source` field tracking origin per record
3. **Deduplication** — detect and handle duplicate records across sources using normalized primary key
4. **Balanced sampling** — use stratified sampling by source to ensure representation from all 3 sources
5. **Post-merge validation** — verify row counts, check for null patterns in normalized columns, report source distribution
6. **Checkpoint with metadata** — save merged result with provenance info (source counts, schema mapping applied)

## Key Differentiators

The skill teaches schema normalization before merge — the critical step that prevents the common failure of `pd.concat()` producing a wide DataFrame full of NaN columns. It also introduces source provenance tracking as a standard practice, which is essential for data lineage and debugging.
