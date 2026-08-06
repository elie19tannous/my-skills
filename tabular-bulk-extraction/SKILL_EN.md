---
name: tabular-bulk-extraction
description: Extract structured tabular data from bulk documents — invoices, fee schedules, rent rolls, cap tables, exhibit indices, expense ledgers, damage schedules — into clean, typed CSV or JSON with a consistent column schema, one row per record, and every value traceable back to its source document and location. Use when a user asks you to pull line items out of many similar documents into a table; to normalize a pile of invoices/statements/exhibits into a single spreadsheet; to build a schedule or index from a document set; or to run a "tabular review" / "bulk extraction" pass. Covers schema definition, per-document field extraction, normalization/typing, cross-document consolidation, and a provenance-carrying output table. Do NOT treat extracted numbers as reconciled totals without checking them against the source, and do NOT silently coerce ambiguous values (blank, "N/A", multi-currency, split cells) — surface them for review rather than guessing.
license: MIT
compatibility: No network required for the workflow or the offline extraction-helper script (Python stdlib only — CSV/JSON parsing, delimiter sniffing, type coercion). OCR of scanned/image PDFs and reading proprietary formats are separate, upstream steps.
---

# Tabular Bulk Extraction

## Instructions

> **Core rule:** the output is only as trustworthy as its provenance. Every extracted cell must carry where it came from (source document + page/row/cell), and any value you could not read cleanly must be emitted as a flagged blank — never a guessed number. Consolidating 200 invoices into one clean table is worthless if three amounts were silently invented.

### Step 1: Define the Target Schema First
Before touching any document, pin down the columns. Extraction without a fixed schema produces ragged, unmergeable output.

| Question | Why it matters |
|----------|----------------|
| What is one row? | The record grain — one invoice, one line item, one exhibit, one lease. Mixing grains breaks totals and dedup |
| What columns, in what order? | Fixed column set + order so every document maps to the same table; late-added columns force a re-run |
| What type is each column? | date / money / integer / text / enum — typing is what makes the table computable, not just a text dump |
| What is the source-provenance column? | Every row needs `source_doc` and a location (page/row/cell) so a value can be traced back and checked |
| What is the unit/currency convention? | One currency and one date format for the whole table; record the original if it differed |

### Step 2: Extract Per Document
Process each source document into rows against the fixed schema.

- Map each source field to exactly one target column; if a source has no value for a column, emit an explicit **blank**, not a zero or a guess.
- Keep the **raw** value alongside the normalized one when they differ (e.g. `"1.234,50 €"` raw → `1234.50` money + `EUR` currency), so normalization is auditable.
- Record the **location** of each row's key value (page, table, row index) in the provenance column.
- One document can yield many rows (an invoice with 12 line items → 12 rows) or one (a cover sheet → 1 row). Decide from the row grain in Step 1.

The bundled `scripts/table_extract.py` sniffs delimiters, parses CSV/TSV/pipe tables and simple JSON, coerces types, and reports per-column blanks/anomalies. Treat its output as a first pass to be reviewed, not a final table.

### Step 3: Normalize and Type
Turn raw strings into computable, comparable values — the step that separates a real extraction from a screenshot.

| Field type | Normalize to | Watch for |
|-----------|--------------|-----------|
| Money | Decimal, single currency, no thousands separators | `1,234.50` vs `1.234,50`; `(500)` = −500; trailing `CR`/`DR`; mixed currencies |
| Date | One ISO format (YYYY-MM-DD) | `03/04/2024` is ambiguous (Mar 4 vs Apr 3) — fix from context, don't guess |
| Integer/quantity | Plain integer | Units embedded in the cell ("12 units"), ranges ("3–5") |
| Enum/status | Controlled vocabulary | Free-text variants ("paid", "PAID", "settled") collapsing to one value |
| Text | Trimmed, whitespace-normalized | Line breaks inside a cell, merged/split cells shifting columns |

If a value cannot be normalized unambiguously (unknown currency, ambiguous date, split cell), keep the raw value AND flag the row — do not force it into a type.

### Step 4: Consolidate Across Documents
Merge the per-document rows into one table.

- Enforce the **same column set and order** for every row; a document missing a column gets blanks, not a shortened row.
- **Deduplicate** on a stable key (invoice number, exhibit ID) — but flag near-duplicates (same number, different amount) rather than dropping one silently.
- Compute **subtotals/totals only if asked**, and mark them as derived; never overwrite an extracted total with your computed one — instead flag a mismatch for reconciliation.
- Preserve row order or sort on an explicit key; record which.

### Step 5: Emit the Table + an Extraction Report
Deliver the data in the requested format (CSV or JSON) plus a short report.

CSV: fixed header row, one record per line, blanks as empty fields (not "N/A"), provenance columns included.
JSON: array of objects with identical keys per object, `null` for blanks, a nested `_source` for provenance.

The report states:

| Field | Content |
|-------|---------|
| Coverage | X documents processed → Y rows; N documents unreadable/skipped (list them) |
| Blanks | Which columns have blanks and how many — a column that is 60% blank may be mis-mapped |
| Anomalies | Rows flagged for review: ambiguous dates, mixed currencies, split cells, near-duplicates, total mismatches |
| Provenance | Confirmation that every row carries a source_doc + location |

End with a headline: "Y rows from X documents; N flagged for review; M unreadable documents." Do not present the table as final while flagged rows remain unresolved.

### Step 6: Anti-Fabrication Discipline
Bulk extraction's failure mode is a clean-looking table with invented cells.

- A cell you could not read is a **flagged blank**, never a plausible number.
- Do not infer a missing amount from surrounding rows or "typical" values.
- Do not silently pick one interpretation of an ambiguous date/currency — flag it.
- Do not drop an unreadable document to make coverage look complete — list it as skipped.
- A computed total is **derived** and labeled as such; it never replaces or masks an extracted total that disagrees.

## Examples

### Example 1: Bulk Invoice Extraction
**Input:** "Pull these 180 vendor invoices (PDF text) into one CSV: invoice no, date, vendor, line item, qty, unit price, amount, currency."
**Output:** Defined the schema with those columns plus `source_doc` and `page`. Extracted 180 documents → 1,412 line-item rows (one row per line item). Normalized 174 invoices to a single currency; 6 were EUR-denominated, kept raw and added a `currency` value of EUR rather than converting. Flagged 9 rows: 4 ambiguous `03/04` dates (resolved 3 from the invoice period, left 1 for review), 3 split-cell descriptions that shifted the amount column, 2 near-duplicate invoice numbers with different totals. 2 invoices were scanned images with no text layer — listed as unreadable, need OCR. Headline: 1,412 rows from 178 documents; 9 flagged; 2 unreadable.

### Example 2: Building an Exhibit Index
**Input:** "Turn this document production into an exhibit index: exhibit no, date, description, Bates start, Bates end, doc type."
**Output:** One row per exhibit. Ran the helper over the export, isolated 96 exhibits. Normalized Bates ranges to `PREFIX-000123` form; 3 exhibits had a start Bates greater than the end (transposed) — flagged, not auto-swapped. 5 exhibits had no date on the face of the document — emitted blank date with a note rather than inferring from filename. Delivered the index sorted by Bates start, with `source_doc` per row. Headline: 96 exhibits indexed; 8 flagged for review; 0 unreadable.

### Example 3: Consolidating Fee Schedules
**Input:** "Merge these 30 quarterly fee schedules into one table and give me the total per quarter."
**Output:** One row per fee line, columns for quarter, fee type, basis, rate, amount, plus provenance. 30 schedules → 640 rows. Computed per-quarter subtotals as clearly-labeled derived rows; for 2 quarters my computed total differed from the schedule's stated total — flagged both as reconciliation items rather than overwriting the stated figure. 4 rows had a rate expressed as a range ("0.5–0.75%") — kept raw and flagged. Headline: 640 rows from 30 documents; 2 total mismatches + 4 range rows flagged; 0 unreadable.

## Bundled Resources

### References
- `references/extraction-workflow.md` -- End-to-end pass: schema-first definition, per-document extraction, the normalization/typing rules (money, date, enum, quantity), cross-document consolidation and dedup, and the output + report format. Consult when running a bulk-tabular pass start to finish.
- `references/schema-and-types.md` -- The column-schema and type taxonomy: choosing the row grain, fixed column order, per-type normalization targets and traps (ambiguous dates, decimal/thousands separators, parenthesized negatives, split/merged cells), provenance columns, and when to keep a raw value alongside the normalized one. Consult when defining the schema or deciding how to type a messy column.

### Scripts
- `scripts/table_extract.py` -- Offline first-pass extraction helper (Python stdlib only, no network). Sniffs the delimiter of a CSV/TSV/pipe-delimited table (or parses a simple JSON array), coerces columns to money/date/integer/text using conservative rules, reports per-column blank counts and anomalies (ambiguous dates, non-numeric money cells, ragged rows), and can emit normalized CSV or JSON. It flags ambiguous cells for human review; it does NOT reconcile totals, convert currencies, OCR images, or guess missing values. Run: `python scripts/table_extract.py --help`

## Gotchas

- No schema, no table. Extracting before fixing the column set and row grain yields ragged output that will not merge across documents. Define the schema first (Step 1).
- A clean table can hide invented cells. The whole risk of bulk extraction is that unreadable values get silently filled. A cell you could not read is a flagged blank, never a plausible number.
- `03/04/2024` is ambiguous. Day/month vs month/day cannot be resolved from the cell alone. Resolve from document context (invoice period, other dates) or flag it — never guess.
- Decimal and thousands separators flip by locale. `1,234.50` (US) and `1.234,50` (EU) are the same amount written oppositely; misreading one is a 1000× error. Detect the convention per document, don't assume.
- Parenthesized or trailing-CR/DR numbers are signed. `(500)` and `500 CR` usually mean −500 in ledgers. Coercing them as positive corrupts every total.
- Split and merged cells shift columns. A description that wraps into the next column silently pushes the amount into the wrong field for that row. This is why provenance + per-column blank counts matter — a column suddenly 40% blank signals a shift.
- Extracted total vs computed total: when they disagree, flag it — do not overwrite the source's stated total with your arithmetic. The mismatch is the finding.
- Near-duplicate ≠ duplicate. Same invoice number with a different amount is a red flag (revised invoice, double billing), not a row to silently drop.
- Scanned/image PDFs have no text layer. The helper reads text tables only; image documents need OCR first and must be listed as unreadable, not omitted to inflate coverage.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| RFC 4180 (CSV format) | https://www.rfc-editor.org/rfc/rfc4180 | The de-facto CSV rules: quoting, embedded commas/newlines, header row — so emitted CSV parses cleanly downstream |
| ISO 8601 (date/time format) | https://www.iso.org/iso-8601-date-and-time-format.html | The unambiguous YYYY-MM-DD date target every extracted date should normalize to |
| ISO 4217 (currency codes) | https://www.iso.org/iso-4217-currency-codes.html | The three-letter currency codes (USD, EUR, ILS) to tag money columns consistently |

## Recommended MCP Servers

These Model Context Protocol servers pair well with this skill:

- **filesystem**: open the bulk document set (the invoices, exhibits, schedules) so each source can be read and its values extracted against the actual text.
- **fetch / web-fetch**: retrieve a reference table or code list (e.g. a currency or unit code list) when normalizing values to a standard.

Reading the source documents is required — provenance and normalization can only be graded against the actual document text, never assumed.

## Troubleshooting

### Error: "A whole column came out mostly blank"
Cause: The source field is named differently across documents, or a split/merged cell shifted values into an adjacent column, so the mapping missed them.
Solution: Check the per-column blank count in the report — a column that is suddenly 40%+ blank almost always signals a mis-mapping or a column shift, not genuinely absent data. Re-map the field name variants, and inspect a few flagged rows for cell shifts before trusting the column.

### Error: "The totals don't tie out"
Cause: Money cells were mis-typed (thousands/decimal separator confusion, or parenthesized negatives read as positive), or extracted and computed totals were conflated.
Solution: Re-check the money normalization per document (Step 3): confirm the separator convention and sign handling. Keep the extracted total and your computed total as separate, labeled values and flag the mismatch — do not overwrite one with the other. The discrepancy is a finding to reconcile, not an error to paper over.

### Error: "Dates are inconsistent or clearly wrong"
Cause: Ambiguous `DD/MM` vs `MM/DD` inputs were coerced with a single assumption, flipping some dates.
Solution: Resolve ambiguous dates from document context (the invoice/statement period, neighboring unambiguous dates like a day > 12), normalize all to ISO YYYY-MM-DD, and flag any that remain ambiguous rather than guessing. Never apply one locale assumption blindly across a mixed set.
