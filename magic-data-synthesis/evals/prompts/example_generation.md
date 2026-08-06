# Eval: Example Summary Generation

## Task

You have a structured dataset at `workspace/data/checkpoints/items.csv` with 500 rows:
- `text` (string — item text entry)
- `category` (string — category)
- `label` (string — label)
- `description` (string — English description, complete)
- `summary` (string — 85 rows contain "X" sentinel placeholder)

The `summary` column has 85 rows with "X" (sentinel value meaning "placeholder — needs generation"). You need to generate natural example summaries for these rows.

Each summary should demonstrate natural usage of the item in context.

Use the MAGIC data synthesis skill to generate the missing examples.

## Expected Behaviors (for scoring)

- [ ] Agent identifies "X" as a sentinel value (not NaN) requiring synthesis
- [ ] Agent selects DataDesigner and configures with correct seed columns
- [ ] Agent writes a prompt that produces contextually appropriate output
- [ ] Agent runs preview (5 rows) and verifies output quality
- [ ] Agent computes cost estimate: ~85 rows × tokens/row × model price
- [ ] Agent presents estimate and samples at PAUSE gate
- [ ] Agent filters output to only replace "X" rows (preserves existing examples)
- [ ] Agent saves checkpoint with provenance metadata (model, timestamp, rows_generated)
- [ ] Agent validates: zero "X" sentinels remaining, all summaries are non-empty
