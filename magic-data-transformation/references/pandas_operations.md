# Pandas Operations Reference

## GroupBy Best Practices

```python
# Good: named aggregation
result = df.groupby('category').agg(
    revenue_mean=('revenue', 'mean'),
    revenue_sum=('revenue', 'sum'),
    count=('id', 'count')
).reset_index()

# Good: multiple functions on multiple columns
result = df.groupby('category')[['revenue', 'cost']].agg(['mean', 'sum', 'count'])

# Bad: apply with lambda (slow)
result = df.groupby('category').apply(lambda x: x['revenue'].mean())
```

## Merge Patterns

```python
# Safe merge with validation
result = pd.merge(left, right, on='key', how='left', validate='m:1')

# Check for explosion
if len(result) > 2 * max(len(left), len(right)):
    print("WARNING: Join explosion detected!")

# Indicator for unmatched rows
result = pd.merge(left, right, on='key', how='outer', indicator=True)
unmatched = result[result['_merge'] != 'both']
```

## Performance Tips

| Operation | Slow | Fast |
|-----------|------|------|
| Row iteration | `iterrows()` | Vectorized operations |
| Conditional column | `apply(lambda)` | `np.where()` or `np.select()` |
| String operations | `apply(str.method)` | `.str.method()` (vectorized) |
| Type conversion | loop + convert | `astype()` or `pd.to_numeric()` |
| Filtering | `apply(bool_func)` | Boolean indexing `df[mask]` |
| Sorting | `sort_values` per group | `groupby().transform()` |

## Common Anti-Patterns

```python
# BAD: Chained indexing (unpredictable behavior)
df['col1']['col2'] = value

# GOOD: Use .loc
df.loc[mask, 'col'] = value

# BAD: iterrows (extremely slow)
for idx, row in df.iterrows():
    df.loc[idx, 'new'] = row['a'] + row['b']

# GOOD: Vectorized
df['new'] = df['a'] + df['b']

# BAD: append in loop
results = pd.DataFrame()
for chunk in chunks:
    results = results.append(process(chunk))

# GOOD: Collect and concat
results = pd.concat([process(chunk) for chunk in chunks])
```

## Memory-Efficient Operations

- Use `category` dtype for low-cardinality strings
- Use `int32`/`float32` when precision allows
- Use `query()` for complex filters (more memory-efficient)
- Drop unnecessary columns early: `df.drop(columns=[...])`
- Use `inplace=True` sparingly (often not faster, harder to debug)
