# Magic Data Visualization

Select appropriate chart types and generate publication-quality visualizations as PNG, SVG, or interactive HTML.

## What This Skill Does

- Recommends chart type (bar, line, scatter, histogram, box, heatmap, small multiples) based on data shape and question
- Generates matplotlib/seaborn static charts and Plotly interactive HTML visualizations
- Validates chart correctness (axis labels, color accessibility, scale appropriateness) before output

## Files

- `SKILL.md` — Agent knowledge document and frontmatter
- `scripts/` — `chart_selector.py`, `generate_chart.py`, `validate_chart.py`

## Related Skills

- `magic-data-profiling` — profiling results are a primary input for visualization
- `magic-statistical-analysis` — visualize statistical findings and significance results
- `magic-report-generation` — charts are embedded in final reports
