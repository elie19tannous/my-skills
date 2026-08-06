# Schema Format Reference

## Schema JSON Structure

```json
{
  "columns": {
    "column_name": {
      "dtype": "numeric|text|categorical|datetime|boolean",
      "nullable": true,
      "constraints": {
        "min": 0,
        "max": 100,
        "pattern": "^[A-Z]{2}$",
        "max_length": 255,
        "allowed_values": ["A", "B", "C"]
      }
    }
  },
  "row_count_range": {
    "min": 100,
    "max": 1000000
  }
}
```

## Constraint Types

| Constraint | Applies To | Description |
|-----------|-----------|-------------|
| `min` / `max` | numeric, datetime | Value range bounds |
| `pattern` | text, categorical | Regex pattern for valid values |
| `max_length` | text | Maximum string length |
| `min_length` | text | Minimum string length |
| `allowed_values` | categorical | Exhaustive list of valid values |
| `unique` | any | Column must have all unique values |
| `not_null` | any | No null values allowed |

## Strict vs Normal Mode

| Aspect | Normal | Strict |
|--------|--------|--------|
| Nullable | true if any nulls exist | false if column has 0 nulls |
| Numeric range | min-max of data | p5-p95 range |
| Allowed values | All observed values | Values with >1% frequency |
| Pattern | Most common pattern | Strict pattern from all values |

## Cross-Column Constraints

```json
{
  "constraints": [
    {
      "type": "comparison",
      "columns": ["start_date", "end_date"],
      "params": {"operator": "<"}
    },
    {
      "type": "conditional_null",
      "columns": ["status", "resolved_date"],
      "params": {"condition": "if status == 'resolved', resolved_date must not be null"}
    },
    {
      "type": "unique_together",
      "columns": ["user_id", "order_date"],
      "params": {}
    },
    {
      "type": "vocabulary",
      "columns": ["country_code"],
      "params": {"allowed": ["US", "CA", "UK", "DE", "FR"]}
    }
  ]
}
```
