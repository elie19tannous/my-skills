# WHO EMT MDS Periodic Report — HTML Template Asset

This asset contains A4 portrait HTML templates for a multi-day WHO EMT MDS Periodic Report.

## Files

- `styles.css` — shared A4 portrait print stylesheet using blue WHO/UN-style visual language.
- `page01_cover_executive_summary.html`
- `page02_reporting_coverage_operational_context.html`
- `page03_demographic_statistics.html`
- `page04_health_events_summary.html`
- `page05_health_events_trends.html`
- `page06_procedures_outcomes.html`
- `page07_relation_protection.html`
- `page08_needs_risks_operational_constraints.html`
- `page09_data_quality_validation.html`
- `appendix_a_daily_breakdown.html`
- `appendix_b_full_mds_item_totals.html`
- `appendix_c_restricted_line_list_trigger_summary.html`

## Template syntax

The files use Mustache/Handlebars-style placeholders:

- Scalar placeholders: `{{total_consultations}}`
- Repeating rows: `{{#daily_coverage_rows}} ... {{/daily_coverage_rows}}`
- Empty-state fallbacks: `{{^daily_coverage_rows}} ... {{/daily_coverage_rows}}`

## A4 print behavior

The stylesheet defines:

```css
@page { size: A4 portrait; margin: 0; }
.report-page { width: 210mm; min-height: 297mm; }
```

Tables that exceed one page should be split by the rendering/generation layer according to the overflow rule: repeat title, repeat table header, add `continued`, preserve columns.

## Confidentiality behavior

The main report pages display aggregated protection and restricted-trigger counts only. `appendix_c_restricted_line_list_trigger_summary.html` is visually marked as restricted and should be generated separately or protected by the consuming system.
