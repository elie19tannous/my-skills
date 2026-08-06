# Magic Data Synthesis

Generate and enrich data using LLM-based operations via the DataDesigner engine — for tasks that require contextual judgment, not just deterministic transformation.

## What This Skill Does

- Fills sentinel and placeholder values (e.g. "TBD", "N/A") with contextually appropriate content using LLM generation
- Translates columns, converts formats (HTML to Markdown), annotates records, and extracts structured data from text
- Generates new columns from existing context (summaries, labels, scores) via configurable prompt templates

## Files

- `SKILL.md` — Agent knowledge document and frontmatter
- `scripts/` — `synthesis_config.py`, `generate_column.py`, `batch_synthesize.py`, `synthesis_prompt_builder.py`, `enrich_from_reference.py`, `validate_synthetic.py`

## Related Skills

- `magic-data-cleaning` — deterministic fixes (whitespace, encoding) belong in cleaning, not synthesis
- `magic-data-validation` — validate synthetic outputs for quality and consistency
- `magic-workspace-init` — LLM configuration required before synthesis can run
