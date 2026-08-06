# Advanced Loading Patterns

## Streaming and Chunked Loading

- When a file exceeds 500MB, use chunked loading with `--chunk_size` to avoid memory exhaustion
- Process each chunk independently: clean, validate, and transform before loading the next chunk
- Concat chunks at the end only if the final combined dataset fits in memory — otherwise write each chunk to output incrementally
- Set chunk size based on available memory: estimate row memory with `df.memory_usage(deep=True).sum()` on a small sample
- When aggregating chunked data, accumulate partial results (running sums, counts) rather than storing all chunks
- For chunked CSV reading: `pd.read_csv(path, chunksize=50000)` returns an iterator — process in a for loop
- Track progress on chunked reads: count chunks processed and log total rows consumed to monitor completion
- For chunked aggregation, maintain running state (sum, count, min, max) across chunks instead of re-reading the file

## Schema-on-Read

- Load all columns as strings first (`dtype=str`), then profile the data before casting to specific types
- This prevents silent coercion: "001" becomes 1 as integer, "NA" becomes NaN, "True" becomes boolean — all losing original meaning
- After profiling, cast columns explicitly: `pd.to_numeric()` with `errors='coerce'` to surface unparseable values as NaN
- For date columns, use `pd.to_datetime()` with `format=` specified explicitly — auto-detection guesses wrong on ambiguous formats
- Document every type casting decision: which columns were cast, what format was assumed, how many values failed to parse
- When a column has mixed types (numbers and strings), keep as string and flag for review rather than forcing numeric
- Compare row count before and after type casting — any reduction means rows were silently dropped or coerced to NaN
- For boolean-like columns ("Yes"/"No", "Y"/"N", "1"/"0"), map explicitly rather than relying on automatic parsing

## Evolving Schemas

- Before merging files from different time periods, compare column names across all files to detect schema changes
- Handle new columns: add them to older datasets as NULL-filled columns so concat works without data loss
- Handle removed columns: decide whether to drop from all files or keep with NULLs — document the decision
- Handle renamed columns: use fuzzy matching (Levenshtein >0.85) on column names to suggest renames, then confirm manually
- Create a schema registry: store expected column names, types, and constraints. Validate each file against it before loading
- When column order differs across files, always merge by column name, never by position
- Log schema evolution over time: which files introduced new columns, which dropped columns — creates an audit trail
- When fuzzy column matching suggests a rename, require explicit user confirmation before applying

## Multi-File Assembly

- Use glob patterns to discover files: `glob.glob('data/sales_*.csv')` — sort the result for deterministic ordering
- Load each file individually, validate schema compatibility before concatenating
- Add a `source_file` column to each DataFrame before concat to enable tracing any row back to its origin file
- Validate schema compatibility: same column names, compatible types, consistent value formats across files
- When files have overlapping data (date ranges), detect and deduplicate overlapping rows after concat
- Log the file manifest: number of files found, rows per file, total rows after concat, any files that failed to load
- For mixed formats (some CSV, some Excel), normalize each to a common DataFrame structure before combining
- Handle encoding differences across files: detect encoding with chardet/charset-normalizer, convert all to UTF-8 before processing
- When loading from nested directories, preserve the directory path in metadata to maintain organizational context
- Validate total row count after assembly: sum of individual file row counts must equal final DataFrame row count
- For very large multi-file loads, process files in batches rather than loading all at once — reduces peak memory usage
- Set a consistent column order after assembly to ensure downstream code does not depend on source file ordering
