# Magic Report Generation

Assemble data analysis findings into structured Markdown reports with mandatory sections and support for standard, executive, and technical templates.

## What This Skill Does

- Converts findings JSON and analysis outputs into formatted Markdown reports with required sections (Summary, Data Provenance, Methodology, Key Findings, Caveats, Next Steps)
- Supports three templates: standard (balanced), executive (brief, stakeholder-facing), and technical (full detail)
- Formats tables, embeds chart references, and validates report completeness before output

## Files

- `SKILL.md` — Agent knowledge document and frontmatter
- `scripts/` — `generate_report.py`, `format_table.py`, `validate_report.py`

## Related Skills

- `magic-statistical-analysis` — statistical findings are a primary report input
- `magic-data-visualization` — charts referenced in reports are generated here
- `magic-data-lifecycle` — report generation is the final deliverable phase of the pipeline
