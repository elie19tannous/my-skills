# Data Cleaning Edge Cases

## Encoding Issues

### BOM (Byte Order Mark)
- **Symptom:** Column name starts with `ï»¿` or invisible characters
- **Fix:** Read with `encoding='utf-8-sig'` to strip BOM
- **Detection:** Check first 3 bytes: `EF BB BF`

### Mojibake (Garbled Characters)
- **Symptom:** `Ã©` instead of `é`, `â€"` instead of `—`
- **Fix:** Re-read with correct encoding (usually Latin-1 or Windows-1252)
- **Detection:** Look for patterns like `Ã` followed by common accented chars

### Mixed Encodings
- **Symptom:** Some rows decode correctly, others don't
- **Fix:** Read with `errors='replace'`, then clean replacement characters
- **Detection:** UnicodeDecodeError on specific rows, not all

## Type Issues

### "N/A" Strings in Numeric Columns
- **Symptom:** `TypeError` when computing statistics on "numeric" column
- **Fix:** Pre-process: `df[col].replace(['N/A', 'null', 'none', 'NULL', '', '-'], np.nan)`
- **Common variants:** "N/A", "NA", "null", "NULL", "None", "none", "-", ".", "unknown", "#N/A", "#VALUE!"

### Mixed Dates
- **Symptom:** Some dates are "2024-01-15", others are "01/15/2024" or "15-Jan-24"
- **Fix:** Use `pd.to_datetime(col, infer_datetime_format=True, errors='coerce')`
- **Detection:** Multiple date patterns in same column

### Numbers as Strings
- **Symptom:** Column should be numeric but contains "$1,234" or "45%"
- **Fix:** Strip currency/percentage symbols, then convert: `col.str.replace('[$,%]', '', regex=True).astype(float)`

## Delimiter Issues

### Semicolon Delimiters
- **Symptom:** Single column with embedded commas, or column count = 1
- **Fix:** Re-read with `sep=';'`
- **Detection:** European CSV files, or count delimiters per line

### Multi-Character Delimiters
- **Symptom:** Columns contain partial delimiter strings
- **Fix:** Use `sep='||'` or appropriate multi-char delimiter
- **Detection:** Check for consistent `||` or `\t\t` patterns

### Embedded Newlines in Quoted Fields
- **Symptom:** Row count much higher than expected, broken rows
- **Fix:** Ensure `quotechar='"'` and `doublequote=True` in pandas read_csv
- **Detection:** Misaligned columns in middle of file

## Content Issues

### Leading/Trailing Whitespace
- **Symptom:** "New York" != "New York " (trailing space)
- **Fix:** `df[col] = df[col].str.strip()`
- **Detection:** `(df[col] != df[col].str.strip()).sum() > 0`

### Invisible Characters
- **Symptom:** Values look identical but don't match
- **Fix:** `df[col] = df[col].str.replace(r'[\x00-\x1f\x7f-\x9f]', '', regex=True)`
- **Detection:** `df[col].str.contains(r'[\x00-\x1f]', regex=True)`

### Nested JSON in CSV Fields
- **Symptom:** Column contains `{"key": "value"}` strings
- **Fix:** Use `json.loads()` to parse, then `pd.json_normalize()` to flatten
- **Detection:** Column values start with `{` or `[`

### Duplicate Headers
- **Symptom:** First data row is column names, or column names repeat
- **Fix:** Set `header=0` and skip duplicate row, or use `header=None` with manual names
- **Detection:** First row values match column names
