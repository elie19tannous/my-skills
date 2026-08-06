# Format Detection Reference Guide

## File Format Signatures

| Format | Extension | Magic Bytes | Content Pattern |
|--------|-----------|-------------|-----------------|
| CSV | .csv | None | Comma-separated values, optional header |
| TSV | .tsv | None | Tab-separated values |
| Parquet | .parquet, .pq | `PAR1` (bytes) | Binary columnar format |
| JSON | .json | `{` or `[` | Object or array |
| JSONL | .jsonl | `{` per line | One JSON object per line |
| Excel | .xlsx | `PK` (ZIP signature) | OpenXML workbook |
| Excel Legacy | .xls | `D0 CF 11 E0` | OLE2 compound document |

## Encoding Detection

### Common Encodings

| Encoding | When to Suspect | Key Indicators |
|----------|----------------|----------------|
| UTF-8 | Default, most common | Multi-byte sequences (0xC0-0xFD leading bytes) |
| UTF-8 BOM | Windows-generated files | First 3 bytes: `EF BB BF` |
| Latin-1 (ISO-8859-1) | European text, accented chars | Bytes 0x80-0xFF as single chars |
| Windows-1252 | Windows office exports | Smart quotes (0x91-0x94), em-dash (0x97) |
| UTF-16 | Excel exports, some APIs | BOM: `FF FE` (LE) or `FE FF` (BE) |
| ASCII | Simple English text | All bytes < 0x80 |

### Detection Strategy

1. Check for BOM (first 2-4 bytes)
2. If no BOM, use `chardet.detect()` on first 100KB
3. If chardet confidence < 0.7, try reading as UTF-8 then Latin-1
4. Report detected encoding with confidence score

### Mojibake Patterns (Misencoded Text)

| Pattern | Cause | Fix |
|---------|-------|-----|
| `Ã©` instead of `é` | Latin-1 read as UTF-8 | Re-read as Latin-1 |
| `â€"` instead of `—` | Windows-1252 read as UTF-8 | Re-read as Windows-1252 |
| `Ã¼` instead of `ü` | Latin-1 read as UTF-8 | Re-read as Latin-1 |
| `ï»¿` at start of file | UTF-8 BOM not stripped | Strip BOM or use `encoding='utf-8-sig'` |

## Delimiter Detection

### Common Delimiters

| Delimiter | Name | When Common |
|-----------|------|-------------|
| `,` | Comma | Default CSV, most data exports |
| `\t` | Tab | TSV files, database exports |
| `;` | Semicolon | European CSV (comma is decimal separator) |
| `|` | Pipe | Legacy system exports, large fields |
| ` ` | Space | Fixed-width or log files |

### Detection Strategy

1. Read first 5 lines of file
2. Use `csv.Sniffer().sniff()` on the sample
3. If Sniffer fails, count occurrences of common delimiters per line
4. Pick delimiter with most consistent count across lines
5. Verify: column count should be consistent across all sample lines

## Header Detection

- **Has header:** First row has different types than subsequent rows (strings vs numbers)
- **No header:** All rows have same types, or first row is clearly data
- Use `csv.Sniffer().has_header()` on first 10 lines

## Large File Handling

| File Size | Recommendation |
|-----------|---------------|
| < 100MB | Load fully into memory |
| 100MB - 500MB | Load with `low_memory=False`, monitor memory |
| 500MB - 2GB | Use chunked reading (`chunksize=100000`) |
| > 2GB | Consider Parquet conversion or database loading |
