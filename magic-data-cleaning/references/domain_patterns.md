# Domain-Specific Cleaning Patterns

## Financial Data

- Round to 2 decimal places AFTER all arithmetic is complete — rounding intermediate steps compounds errors
- Strip currency symbols and thousand separators before conversion: `col.str.replace(r'[$,]', '', regex=True).astype(float)`
- Handle negative values in parentheses: `(500.00)` means `-500.00` — detect and convert with regex before numeric parsing
- Watch for mixed currency in the same column — split by currency, process separately, convert if needed
- Validate that summed line items equal stated totals — flag rows where abs(sum - total) > 0.01
- Handle percentage representations: some sources use 0.15 (decimal), others use 15 (whole number) — standardize to one format
- Remove leading zeros from account numbers only when confirmed they are non-significant — in some systems "007" differs from "7"

## Date and Time Data

- Normalize all dates to ISO 8601 format (`YYYY-MM-DD`) as the first cleaning step
- When timezone info is missing, document the assumed timezone and apply it explicitly with `tz_localize()`
- For ambiguous formats like `01/02/03`, check the data source documentation. If unavailable, inspect values >12 to infer month position
- Convert `dayfirst=True` for European sources, `dayfirst=False` for US sources — set explicitly, never rely on defaults
- Handle Excel serial dates (integers like 44927) by converting with `pd.to_datetime(col, origin='1899-12-30', unit='D')`
- Strip time components when only date is meaningful — avoids false mismatches due to midnight vs noon timestamps
- Detect and handle mixed date formats within a single column — parse with `errors='coerce'`, then inspect NaT rows for alternate formats
- When merging datasets with dates, ensure both are timezone-aware or both are timezone-naive — mixing causes comparison failures

## Text Deduplication

- Apply deduplication in stages: exact match first, then lowercase+strip, then fuzzy, then manual review
- For fuzzy matching, use Levenshtein ratio >0.85 as the threshold — below that produces too many false positives
- Always preview fuzzy dedup results on a sample before applying to the full dataset — show matched pairs for human review
- For names, normalize "Robert"/"Bob"/"Rob" using a nickname lookup table before fuzzy matching
- Group duplicates and keep the most complete record (fewest NULLs) as the canonical version
- Track dedup decisions: log which records were merged and which were kept — enables auditing and rollback

## Address and Name Data

- Normalize case to title case for names (`str.title()`), uppercase for postal codes
- Expand common abbreviations: St→Street, Ave→Avenue, Dr→Drive, Apt→Apartment. Use a lookup dictionary
- For multi-part surnames (van der Berg, O'Connor, McDonald), do not blindly apply title case — use a name-aware parser
- Standardize phone numbers to E.164 format: strip spaces/dashes/parens, prepend country code if missing
- Split concatenated address fields (full address in one column) only when downstream tasks require it — splitting introduces errors
- For email addresses: lowercase the entire address, validate format with regex, check for common typos (gmial→gmail, yaho→yahoo)
- Validate ZIP/postal codes against expected patterns for the country: US=5 or 9 digits, UK=alphanumeric, CA=alternating letter-digit

## Encoded Values

- Run encoding cleanup BEFORE other string operations — encoded characters break pattern matching and dedup
- Decode HTML entities: `&amp;` → `&`, `&lt;` → `<`, `&#39;` → `'`. Use `html.unescape()` from the standard library
- Decode URL encoding: `%20` → space, `%26` → `&`. Use `urllib.parse.unquote()`
- Apply Unicode normalization (NFC form) to ensure equivalent characters compare as equal: `unicodedata.normalize('NFC', text)`
- Detect and remove BOM (byte order mark) characters at the start of files — they cause invisible column name mismatches
- Replace smart quotes (`\u2018`, `\u2019`, `\u201C`, `\u201D`) with standard ASCII quotes for consistency
- Strip zero-width characters (zero-width space, zero-width joiner) — they are invisible but break string matching and dedup
- Normalize whitespace: collapse multiple spaces to single, replace non-breaking spaces with regular spaces
- Detect mojibake (garbled encoding like "Ã©" instead of "e") — re-decode with the correct source encoding when detected
