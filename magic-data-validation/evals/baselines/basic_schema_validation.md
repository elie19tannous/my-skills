# Baseline: Basic Schema Validation

## Minimum Acceptable Behavior

A competent agent guided by SKILL.md should:

1. **Infer schema from the full dataset** -- not just sample rows. The SKILL.md warns: "NEVER infer schema from only the first few rows."

2. **Follow validation ordering** -- schema validation first, then constraints. The agent should not jump directly to content checking before verifying structure.

3. **Detect structural issues:**
   - 12 null `customer_id` values (nullable=false violation)
   - Type conformance for all columns
   - `status` column has a fixed set of allowed values

4. **Detect constraint violations:**
   - Negative `order_total` values (range constraint: min >= 0)
   - `email` pattern validation (should match email regex)

5. **Produce a structured report** with violation counts and sample values per column.

## Key Knowledge Signals

The agent demonstrates SKILL.md knowledge if it:
- Mentions validation ordering (schema -> constraints -> content -> sanity)
- Distinguishes between schema validation and constraint checking as separate steps
- Does not apply numeric rules to text columns
- Produces a JSON-structured report (not just prose)

## Common Failure Modes

- Agent infers schema from first 10 rows only -- misses issues in later rows
- Agent skips schema inference and jumps to ad-hoc checks
- Agent applies a single monolithic validation pass instead of layered ordering
- Agent flags `email` column with numeric range rules
