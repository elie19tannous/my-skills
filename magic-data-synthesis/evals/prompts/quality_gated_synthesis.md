# Eval: Quality-Gated Synthesis with LLM Judge

## Task

You have a dataset at `workspace/data/checkpoints/items_to_describe.csv` with 50 rows:
- `text` (string — item text entry)
- `category` (string — category)
- `label` (string — label)
- `domain` (string — one of: "daily", "formal", "technical", "informal")

You need to generate HIGH-QUALITY English descriptions with quality scoring. Requirements:
1. Generate a `description` column with English descriptions
2. Add quality scoring with rubrics for: accuracy, completeness, register-appropriateness
3. Only accept descriptions scoring ≥ 70% across all rubrics
4. Re-generate any rows that fail the quality threshold

Use the MAGIC data synthesis skill with DataDesigner's LLMJudge capability.

## Expected Behaviors (for scoring)

- [ ] Agent configures DataDesigner with BOTH text generation AND judge columns
- [ ] Agent defines meaningful rubrics (accuracy, completeness, register) — not generic "quality"
- [ ] Agent uses score scales appropriate to the task (e.g., 0-4 or 0-2)
- [ ] Agent runs preview to check both generated descriptions AND judge scores
- [ ] Agent uses `extract_dd_quality()` or equivalent to interpret judge output
- [ ] Agent applies threshold: mean_100 ≥ 70% to determine pass/fail
- [ ] Agent identifies rows below threshold and proposes re-generation strategy
- [ ] Agent iterates: modifies prompt or adds few-shot examples if quality is low
- [ ] Agent checkpoints only AFTER quality gate passes
- [ ] Agent reports final quality metrics (mean score, pass rate, distribution)
