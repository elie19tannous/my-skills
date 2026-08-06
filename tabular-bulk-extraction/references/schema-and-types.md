# Schema and Types — Building a Mergeable Table

A bulk extraction is only mergeable and computable if every document maps to the
same fixed schema with the same types. This taxonomy is how you fix the schema
and decide how to type a messy column.

## Choosing the row grain

The single most important decision. One row must mean one thing across the whole
set.

| Grain | One row = | Use when |
|-------|-----------|----------|
| Document | one source file | cover sheets, indices (one exhibit per doc) |
| Line item | one line within a document | invoices, schedules, ledgers (many lines per doc) |
| Event | one transaction/entry | statements, transaction logs |

Mixing grains (some rows = whole invoice, some = line item) breaks totals and
dedup. Pick one and hold it.

## Fixed column order

Every document produces rows with the SAME columns in the SAME order, including
blanks for columns a given document lacks. This is what lets 200 documents stack
into one table. Adding a column late means re-running every document.

Always include provenance columns:
- `source_doc` — the file/document identifier.
- a location — `page`, `table`, and/or `row` index so a value can be traced back.

## Type taxonomy and normalization targets

| Type | Target form | Normalization traps |
|------|-------------|---------------------|
| Money | Decimal, one currency, no thousands separators | `1,234.50` (US) vs `1.234,50` (EU) are the same amount; `(500)` and `500 CR`/`DR` are negative; a stray currency symbol; mixed currencies in one column |
| Date | ISO `YYYY-MM-DD` | `03/04/2024` = Mar 4 or Apr 3 — ambiguous; a day > 12 disambiguates, otherwise use context or flag; 2-digit years; Excel serial numbers |
| Integer / quantity | Plain integer | units embedded in the cell ("12 units"), ranges ("3–5"), thousands separators |
| Enum / status | Controlled vocabulary | case + spelling variants ("paid"/"PAID"/"Settled") collapsing to one canonical value |
| Text | Trimmed, whitespace-collapsed | in-cell line breaks, leading/trailing spaces, merged cells |

## When to keep a raw value

Keep the raw string alongside the normalized value whenever normalization is
lossy or judgment-based:
- money where the currency/format was inferred (`"1.234,50 €"` raw → `1234.50` + `EUR`),
- dates resolved from context,
- any cell you flagged as ambiguous.

The raw value is the audit trail: it lets a reviewer confirm the normalization
was right without re-opening the source.

## Split and merged cells

The quiet corruptor. A description that wraps into the neighboring column pushes
every following value one column right for that row — so the amount lands in the
wrong field. Detect it via per-column blank counts: a column that jumps to 40%+
blank on a subset of documents is usually a column shift, not absent data. Never
trust a shifted row; flag and re-map it.

## Provenance is not optional

A value without a source location cannot be checked, and an unverifiable
extraction is exactly the fabrication risk this skill exists to prevent. Every
row carries where it came from; a row that cannot be traced back is itself a flag.
