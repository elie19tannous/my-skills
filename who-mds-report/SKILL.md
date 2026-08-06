---
name: who-mds-report
description: Generate one final WHO Emergency Medical Team Minimum Data Set (MDS) PDF report from a structured Markdown summary created by who-mds-summary. Use when Codex needs to assemble a print-ready PDF in the style of the bundled A4 HTML page templates, include or exclude restricted appendix pages as authorized, or validate final report content from summarized WHO EMT MDS data.
---

# WHO MDS Report

## Inputs

- A structured WHO MDS Markdown summary containing metadata, assumptions, findings, daily coverage, source data, MDS totals, quality checks, and restricted trigger records.
- Optional deployment context supplied by the user, such as organization name, EMT name, reporting period, country, facilities, or intended audience.

## References And Assets

- `references/who_emt_mds_periodic_report_structure.md` defines the report structure, page order, confidentiality rules, and expected report sections.
- `assets/html-report-templates/` contains the canonical A4 page templates and stylesheet. Each HTML template represents one PDF page or appendix page.
- Template placeholders use Mustache-style names. Values come from the Markdown summary or from explicit user-provided context.
- No bundled report script exists by design. Any suitable file-editing, rendering, or PDF-generation method may be used as long as the template assets, summary data, page order, and validation rules are respected.

## Template Mapping

The HTML templates define the visual style and page intent for the final PDF. The Markdown summary defines source values. Placeholder values are copied exactly from matching metadata fields, summary tables, or explicit user context.

Markdown interpretation:

- A two-column table under `## Metadata` maps `Field` to `Value`; field names become scalar placeholders.
- A table under any other `##` heading maps to a row collection; table headers become row keys.
- Heading names are normalized to placeholder collection names by lowercasing and replacing spaces with underscores, with `_rows` appended when the template expects a list.
- Empty sections resolve to `No data available for the selected reporting period.` when the page needs visible content.

Example mappings:

- `{{organization_name}}` receives the `organization_name` value from the `Metadata` table.
- `{{start_date}}` and `{{end_date}}` receive the reporting dates from `Metadata`.
- `{{total_consultations}}`, `{{active_reporting_days}}`, `{{source_file_count}}`, and quality-check placeholders receive exact values from `Metadata`.
- `{{#daily_coverage_rows}}...{{/daily_coverage_rows}}` receives one row per Markdown table row under `Daily Coverage`.
- `{{#top_health_event_rows}}...{{/top_health_event_rows}}` receives rows from `Top Health Events`.
- `{{#restricted_record_rows}}...{{/restricted_record_rows}}` receives rows from `Restricted Trigger Records` only in the restricted appendix, never in the public report.

Minimal transformation example: a `Metadata` row `organization_name | Polish Medical Mission` renders `{{organization_name}}` as `Polish Medical Mission`; a `Top Health Events` row with `rank=1`, `mds_label=Acute respiratory infection`, and `count=74` expands `{{#top_health_event_rows}}...{{/top_health_event_rows}}` once with those row values.

## Assembly Steps

1. Input review: the Markdown summary is checked for the required sections: `Metadata`, `Daily Coverage`, `Source Data`, `Top Health Events`, `Data Quality` or equivalent quality fields, and `Restricted Trigger Records`.
2. Page plan: each required HTML template is treated as one PDF page, in the order defined by `references/who_emt_mds_periodic_report_structure.md`.
3. Template population: the HTML page templates in `assets/html-report-templates/` are filled with exact values from the summary and explicit user context; empty standard sections receive `No data available for the selected reporting period.`.
4. Confidentiality check: public pages remain aggregated and contain no patient identifiers, clinical narratives, line-list trigger records, or protection details; restricted appendix pages are included in the same final PDF only when authorized.
5. PDF assembly: populated HTML pages are rendered into one PDF file, preserving the A4 page styling and one-template-per-page structure.
6. Output validation: the final PDF exists, is non-empty, preserves page order, has no unresolved `{{placeholder}}` markers in its source pages, and contains no unsupported inference beyond the summary.
7. Error recovery: if validation fails, the unresolved placeholder, missing section, confidentiality issue, rendering problem, or unsupported inference is corrected from the Markdown summary or user context, then validation repeats before delivery.
