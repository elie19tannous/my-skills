# Bulk Tabular Extraction Workflow

A repeatable pass for turning many similar documents (invoices, schedules,
exhibits, ledgers) into one clean, typed, provenance-carrying table. The failure
mode this guards against is a tidy-looking spreadsheet with silently invented or
mis-typed cells.

## 0. Schema first

Decide before reading any document:
- Row grain: what is ONE row (one invoice / one line item / one exhibit / one lease).
- Column set + order: fixed for every document; late columns force a re-run.
- Per-column type: date / money / integer / enum / text.
- Provenance columns: `source_doc` + a location (page / row / cell).
- Unit + currency + date conventions for the whole table (record originals if they differ).

## 1. Extract per document

- Map each source field to exactly one target column.
- Missing value → explicit blank, never a zero or a guess.
- Keep the raw value beside the normalized one when they differ (audit trail).
- Record each row's location in the provenance column.
- One document may yield many rows or one — follow the row grain.

## 2. Normalize + type (the load-bearing step)

| Type | Normalize to | Trap |
|------|--------------|------|
| Money | Decimal, one currency, no thousands sep | `1,234.50` vs `1.234,50`; `(500)`/`CR` = negative |
| Date | ISO YYYY-MM-DD | `03/04` ambiguous — resolve from context or flag |
| Integer | Plain integer | units in-cell ("12 units"), ranges ("3–5") |
| Enum | Controlled vocabulary | "paid"/"PAID"/"settled" → one value |
| Text | Trimmed, whitespace-normalized | in-cell line breaks, split/merged cells |

Rules:
- Cannot normalize unambiguously → keep raw AND flag the row; never force a type.
- Detect the decimal/thousands convention per document; do not assume one globally.
- Parenthesized or trailing CR/DR numbers are signed — read the sign.

## 3. Consolidate across documents

- Same column set + order for every row; missing column → blanks, not a short row.
- Dedup on a stable key (invoice no, exhibit ID); flag near-duplicates (same key, different amount) — don't drop silently.
- Totals only if asked, labeled as derived; never overwrite an extracted total with a computed one — flag mismatches.
- Preserve or sort on an explicit key; record which.

## 4. Emit + report

Output (CSV or JSON):
- CSV: fixed header, one record per line, blanks = empty field (not "N/A"), provenance columns included.
- JSON: array of uniform objects, `null` for blanks, nested `_source` for provenance.

Report:
- Coverage: X documents → Y rows; N unreadable/skipped (list them).
- Blanks: per-column blank counts (a 60%-blank column may be mis-mapped).
- Anomalies: flagged rows (ambiguous date, mixed currency, split cell, near-dup, total mismatch).
- Provenance: confirm every row has source_doc + location.
- Headline: "Y rows from X documents; N flagged; M unreadable."

## 5. Anti-fabrication

- Unreadable cell → flagged blank, never a plausible number.
- Never infer a missing amount from neighbors or "typical" values.
- Never silently pick one reading of an ambiguous date/currency — flag it.
- Never drop an unreadable document to inflate coverage — list it.
- Computed totals are derived and labeled; they never mask a disagreeing extracted total.
