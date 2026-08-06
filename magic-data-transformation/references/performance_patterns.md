# Transformation Performance Patterns

## Window Functions

- Use `groupby().transform('mean')` when you need a group-level statistic broadcast back to every row (e.g., deviation from group mean)
- Use `rolling(window=N).mean()` when you need a sliding window calculation over ordered data (time series smoothing)
- Use `expanding().sum()` for cumulative sums that grow with each row
- Use `groupby().rank()` to rank rows within each group — pass `method='dense'` to avoid gaps in rankings
- When combining group and window: first `groupby()`, then `.rolling()` within each group to avoid cross-group contamination
- Prefer `transform()` over `apply()` for element-wise group operations — transform is vectorized and 10-100x faster
- Use `shift()` within groups for lag/lead calculations: `groupby('id')['value'].shift(1)` gives previous row per group
- For percentile within group, use `groupby().transform(lambda x: x.rank(pct=True))` — gives 0-1 percentile rank
- When window functions produce NaN at edges (first N rows), decide upfront: drop, fill with first valid, or leave NaN
- For exponentially weighted calculations, use `ewm()` — gives more weight to recent values than `rolling()`

## Large Data Performance (>1M Rows)

- Convert string columns to `category` dtype when cardinality is <50% of row count — reduces memory by up to 10x
- For joins on large frames, use `merge()` not `apply()` — merge is implemented in C, apply is Python-level looping
- Process in chunks when a single operation would exceed available memory: read chunks, transform each, concat results
- Avoid `apply()` on large DataFrames — use vectorized operations (`np.where`, `.str` accessors, `pd.cut`) instead
- Set join keys as index before merge with `set_index()` — indexed merges are significantly faster
- Use `nsmallest()`/`nlargest()` instead of `sort_values().head()` — avoids full sort
- Use `query()` for filtering: `df.query('age > 30 & city == "NYC"')` is faster and more readable than chained boolean masks
- Pre-filter rows before expensive operations (string parsing, date conversion) — transform only the rows you need
- For conditional logic, use `np.select()` for multiple conditions instead of nested `np.where()` — cleaner and equally fast
- When reading Parquet files, use column pruning and predicate pushdown: `pd.read_parquet(path, columns=[...], filters=[...])`

## Memory Optimization

- Downcast numeric types after loading: `pd.to_numeric(col, downcast='integer')` converts int64 to int8/int16 where possible
- Use `usecols` parameter when reading files to load only needed columns — especially for wide datasets (>50 columns)
- Drop intermediate DataFrames with `del df_temp` and call `gc.collect()` in long transformation pipelines
- Use `float32` instead of `float64` when precision beyond 7 significant digits is unnecessary
- Chain operations without storing intermediates: `df.pipe(step1).pipe(step2).pipe(step3)` avoids extra copies
- Monitor memory during transformations: `df.info(memory_usage='deep')` shows actual memory including string content
- For boolean columns, use `bool` dtype instead of `int64` — saves 7 bytes per value

## Common Bottlenecks and Fixes

- String operations on large frames: convert to `category` first, or use `pyarrow` string dtype for 2-5x speedup
- Many-to-many joins producing row explosion: filter both sides before joining to reduce the cartesian product
- Pivot on high-cardinality columns: aggregate first to reduce unique values, or use `pivot_table` with `aggfunc` to handle duplicates
- Repeated filtering: create a boolean mask once, reuse it, instead of re-evaluating the condition
- GroupBy on string keys: convert to categorical before grouping — groupby on categoricals is faster than on strings
- Chained indexing (`df[cond]['col'] = val`): use `.loc[cond, 'col'] = val` to avoid copies and SettingWithCopyWarning
- Concatenating in a loop (`df = pd.concat([df, new_row])`): collect all pieces in a list first, concat once at the end
- Unnecessary copies from `df.copy()`: only copy when you need to modify a slice independently — otherwise it doubles memory
