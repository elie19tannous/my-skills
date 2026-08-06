---
name: who-mds-summary
description: Aggregate WHO Emergency Medical Team Minimum Data Set (MDS) daily CSV exports into a structured Markdown summary. Use when Codex needs to combine one or more WHO EMT MDS CSV files or folders, calculate multi-day consultation totals, demographics, MDS item counts, data-quality checks, restricted-trigger rows, or prepare summarized input for the who-mds-report skill.
---

# WHO MDS Summary

## Core Contract

Aggregate daily WHO EMT MDS CSV exports into one deterministic Markdown summary file. Do not generate the final report in this skill. The output can be reviewed directly or passed to `who-mds-report`.

## Reference Loading

Read `references/who_emt_mds_periodic_report_structure.md` before changing MDS calculation rules, confidentiality handling, or summary fields.

## Script

Use `scripts/generate_mds_summary.py` for CSV aggregation into Markdown.

Run:

```bash
python scripts/generate_mds_summary.py <csv-file-or-directory> --output who-mds-summary.md
```

Useful options:

```bash
python scripts/generate_mds_summary.py <input> \
  --start-date 2024-05-07 \
  --end-date 2024-05-14 \
  --organization "Polish Medical Mission" \
  --team-name "PMM EMT" \
  --emt-type "Type 1 Fixed" \
  --output who-mds-summary.md
```

The script accepts multiple CSV files and directories. Directories are scanned recursively for `*.csv`.

## Output File

The Markdown file contains metadata, assumptions, findings, daily coverage, demographic and MDS totals, source data, quality checks, and a restricted trigger records section. Treat the restricted trigger records section as confidential when it contains rows.

## Workflow

1. Confirm the requested reporting period and metadata overrides.
2. Run the summary generator on the source MDS CSV files or directory.
3. Validate the summary file before reporting success:

```bash
python scripts/generate_mds_summary.py <input> --output who-mds-summary.md
python -c "from pathlib import Path; p=Path('who-mds-summary.md'); text=p.read_text(encoding='utf-8'); required=['## Metadata','## Daily Coverage','## Source Data','## Restricted Trigger Records']; missing=[name for name in required if name not in text]; raise SystemExit('missing summary sections: '+', '.join(missing)) if missing else print('summary sections present')"
```

4. Compare `source_file_count` in the metadata section with the intended selected inputs, and review the restricted trigger records section through the approved confidential pathway when it contains rows.
5. If validation fails, correct the input selection, date range, or metadata flags, re-run the generator, and repeat validation before using the summary bundle.
6. Pass the Markdown summary file to `who-mds-report` when a final PDF report is needed.

## Calculation Rules

- Treat each CSV row as one consultation unless the user provides a different official aggregation rule.
- Use `h` as the activity date when available.
- Use `MDSa`, `Age`, and `M/Y` to derive age group and under-5 or 5-plus totals.
- Use `MDS1-3` as the sex category: `1` male, `2` female non-pregnant, `3` female pregnant.
- Treat `MDS4` through `MDS65` as binary checkbox-style fields. Values of `1`, `true`, `yes`, `y`, `x`, or `checked` count as selected.
- Keep protection indicators and restricted triggers aggregated in public summary fields. Put restricted line-list trigger rows only in the `Restricted Trigger Records` section.
