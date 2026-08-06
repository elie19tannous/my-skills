# Chart Selection Matrix

## By Data Relationship

| Relationship | Best Chart | Also Good | Avoid |
|-------------|-----------|-----------|-------|
| Distribution (1 numeric) | histogram | kde, box, violin | pie |
| Distribution (1 categorical) | horizontal_bar | bar | pie, 3D bar |
| Comparison (categories × numeric) | grouped_bar | box, violin | pie, 3D |
| Trend (time × numeric) | line | area, scatter | bar (for dense time) |
| Correlation (2 numeric) | scatter | heatmap (many pairs) | line |
| Composition (parts of whole) | stacked_bar | horizontal_bar | pie, 3D pie |
| Ranking (top/bottom N) | horizontal_bar | bar | pie |
| Part-to-whole (few categories) | horizontal_bar | stacked_bar | pie, donut |
| Relationship (many pairs) | heatmap | pair_plot | individual scatters |
| Text (word frequency) | word_frequency_bar | horizontal_bar | word cloud |
| Text (length distribution) | histogram | kde, box | pie |
| Deviation from baseline | bar (diverging) | lollipop | pie |
| Flow/change | slope chart | line | area (misleading) |
| Geospatial | choropleth | scatter_map | bar |

## By Column Count

| Columns | Relationship | Recommended |
|---------|-------------|-------------|
| 1 numeric | Distribution | histogram, box |
| 1 categorical | Frequency | horizontal_bar |
| 2 numeric | Correlation | scatter |
| 1 categorical + 1 numeric | Comparison | grouped_bar, box |
| 1 datetime + 1 numeric | Trend | line |
| 2 categorical | Cross-tabulation | heatmap |
| Many numeric | Overview | heatmap (correlations) |

## Anti-Recommendations

### Never Use
1. **3D charts** — distort perception, always use 2D alternatives
2. **Pie charts** — use horizontal bar instead (easier to compare)
3. **Dual-axis charts** — use facets or separate charts instead
4. **Donut charts** — same problems as pie charts
5. **Exploded pie** — even worse than regular pie
6. **3D bar charts** — perspective makes comparison impossible

### Avoid When
- **Area charts** with >3 overlapping series — use line instead
- **Stacked bar** with >5 categories — too hard to read
- **Scatter** with >10K points without transparency — use hex bins or kde
- **Bar charts** for continuous data — use histogram instead

## Chart Anatomy

Every chart MUST have:
- Clear, descriptive title
- Labeled axes with units (if applicable)
- Legend (when multiple series/groups)
- Readable font sizes (min 10pt)
- Colorblind-safe palette

Every chart MUST NOT have:
- Chart junk (unnecessary decorations)
- Excessive gridlines (light background grid is OK)
- Truncated y-axis (start at 0 for bar charts)
- Misleading scales
