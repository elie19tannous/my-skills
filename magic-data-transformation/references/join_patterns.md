# Join Patterns Reference

## Join Types

| Type | Keeps | Use When |
|------|-------|----------|
| `inner` | Rows with matching keys in BOTH tables | Only want matched records |
| `left` | ALL rows from left + matching from right | Enriching left table with right |
| `right` | Matching from left + ALL rows from right | Enriching right table with left |
| `outer` | ALL rows from both (NaN for non-matches) | Want complete picture of both tables |
| `cross` | Every combination (cartesian product) | Rarely — combinatorial analysis |

## Join Explosion Detection

**Definition:** Output has significantly more rows than either input due to many-to-many key relationships.

**Detection rule:** `rows_out > 2 * max(rows_left, rows_right)`

### Pre-Join Checks

```python
# Check key cardinality
left_key_unique = left[key].nunique()
right_key_unique = right[key].nunique()
left_key_dupes = left[key].duplicated().sum()
right_key_dupes = right[key].duplicated().sum()

# If BOTH sides have duplicates on the key, explosion is likely
if left_key_dupes > 0 and right_key_dupes > 0:
    print("WARNING: Many-to-many join likely — consider deduplicating one side")
```

### Common Explosion Scenarios

| Scenario | Left Rows | Right Rows | Join Key | Result Rows | Problem |
|----------|-----------|------------|----------|-------------|---------|
| 1:1 | 1000 | 1000 | unique | 1000 | None |
| M:1 | 1000 | 100 | left has dupes | 1000 | None |
| 1:M | 100 | 1000 | right has dupes | 1000 | None |
| M:M | 1000 | 1000 | both have dupes | 100K+ | EXPLOSION |

### Mitigation Strategies

1. **Deduplicate before joining:** Pick one row per key (first, last, max, etc.)
2. **Aggregate before joining:** Summarize to one row per key
3. **Use validate parameter:** `pd.merge(..., validate='m:1')` raises on unexpected M:M
4. **Filter after joining:** Remove duplicate combinations
5. **Use different join key:** Find a more specific key with fewer duplicates

## Unmatched Row Analysis

After every join, report:
- `matched`: rows with keys in both tables
- `unmatched_left`: left rows with no match in right
- `unmatched_right`: right rows with no match in left

```python
result = pd.merge(left, right, on='key', how='outer', indicator=True)
matched = (result['_merge'] == 'both').sum()
unmatched_left = (result['_merge'] == 'left_only').sum()
unmatched_right = (result['_merge'] == 'right_only').sum()
```

High unmatched counts may indicate:
- Key naming differences ("ID" vs "id" vs "Id")
- Leading/trailing whitespace in keys
- Different date formats
- Missing values in key columns
