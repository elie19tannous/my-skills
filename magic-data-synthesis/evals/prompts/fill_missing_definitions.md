# Eval: Fill Missing Definitions (DataDesigner)

## Task

You have a CSV file at `workspace/data/input/items.csv` with 100 rows:
- `text` (string, complete — product items)
- `category` (string, complete)
- `label` (string, complete)
- `description` (string, 30 rows are null/empty)

The `description` column has 30 missing values. You need to generate English descriptions for these items based on the text, category, and label.

Use the MAGIC data synthesis skill to fill in the missing descriptions.

## Expected Behaviors (for scoring)

- [ ] Agent assesses feasibility: confirms that description generation requires contextual understanding, making LLM synthesis appropriate (not regex)
- [ ] Agent selects DataDesigner as the synthesis engine (not legacy batch_synthesize)
- [ ] Agent picks a recipe template (e.g., text_generation_template.py or text_generation_gemini_template.py)
- [ ] Agent edits the template: sets seed path, adjusts prompt to reference {{ text }}, {{ category }}, {{ label }}
- [ ] Agent runs `data-designer validate` on the config before proceeding
- [ ] Agent runs `data-designer preview --num-records 5` to verify output quality
- [ ] Agent presents preview results + cost estimate and waits for user approval (PAUSE gate)
- [ ] Agent runs `data-designer create` only after approval
- [ ] Agent saves output as MAGIC checkpoint via save_checkpoint()
- [ ] Agent validates output (non-empty descriptions, no sentinels remaining)
