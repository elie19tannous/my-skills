# Large File Loading Patterns

## When to Use Chunked Loading

- File size > 500MB
- Available RAM < 2x file size
- MemoryError on standard `pd.read_csv()`
- Processing can be done incrementally (aggregations, filtering)

## Chunked Reading Pattern

```python
chunks = pd.read_csv(path, chunksize=100000, encoding=encoding)
results = []
for chunk in chunks:
    processed = process_chunk(chunk)
    results.append(processed)
final = pd.concat(results)
```

## Chunk Size Selection

| Available RAM | Recommended Chunk Size | Approx Rows (10 cols) |
|---------------|----------------------|----------------------|
| 2GB | 50,000 | 50K rows |
| 4GB | 100,000 | 100K rows |
| 8GB | 250,000 | 250K rows |
| 16GB+ | 500,000 | 500K rows |

## Memory-Efficient Data Types

| Standard Type | Efficient Type | Savings |
|--------------|---------------|---------|
| int64 | int32 or int16 | 50-75% |
| float64 | float32 | 50% |
| object (low cardinality) | category | 90%+ |
| object (dates) | datetime64 | 50%+ |

## Strategies for Large Files

1. **Sample first**: Use `sample_rows.py --n 1000` to understand data
2. **Subset columns**: Use `usecols` parameter to load only needed columns
3. **Filter early**: Apply row filters during chunked reading
4. **Convert format**: Save as Parquet for 5-10x smaller files with faster loading
5. **Aggregate during load**: Compute aggregations per chunk, merge at the end
