# Advanced Visualization Patterns

## Large Dataset Strategies (>100K Points)

- When scatter plot has >100K points, switch to hexbin or 2D density plot — individual points become meaningless noise
- For exploratory analysis on large data, sample 10K points randomly to find patterns, then confirm on full dataset
- For presentation charts on large data, aggregate first: mean/median per bin, per time period, or per category
- Never render >50K points in interactive plots — browser will lag. Use static rendering or server-side aggregation
- When using sampling, add a note to the chart: "Showing N of M points (random sample)"
- For heatmaps on large data, bin both axes — do not create a cell per unique value or the chart becomes unreadable
- Use data reduction before plotting: pre-aggregate with groupby, resample time series to coarser frequency
- When comparing distributions of large datasets, use violin plots or boxplots instead of overlapping histograms

## Small Multiples (Faceting)

- Use facets (small multiples) instead of overlaying when there are >3 categories on the same axis
- Use facets when overlapping lines/bars obscure the pattern you want to show
- Use overlay when comparing 2-3 series directly and the ranges are similar
- Keep facet grid to max 3x4 (12 panels) — beyond that, consider grouping categories
- Share axes across facets so readers can compare magnitudes across panels
- When faceting by time, keep chronological order. When faceting by category, order by a meaningful metric (descending value)
- Label each facet panel clearly with the category value — do not rely on a shared legend for facet identity
- When comparing faceted distributions, use consistent bin widths across all panels

## Annotation Best Practices

- Annotate outliers that the audience will ask about — preempt "what's that spike?" questions
- Annotate inflection points where trends change direction — these are the story
- Annotate threshold lines (targets, limits, baselines) with labels, not just horizontal lines
- Limit to max 5 annotations per chart — more than that creates clutter and defeats the purpose
- Place annotation text to avoid overlapping data points. Use leader lines when needed
- For time series, annotate known events (product launches, policy changes) that explain shifts

## Log Scale Guidance

- Use log scale when data spans >2 orders of magnitude (e.g., values from 10 to 10,000)
- Always label the axis clearly as "log scale" — readers will misinterpret linear-looking log charts
- Use log scale for rate-of-change comparisons: equal slopes = equal growth rates
- Do not use log scale when zero or negative values exist in the data — log(0) is undefined
- When presenting to non-technical audiences, prefer breaking into separate charts over using log scale
- For dual-range data, consider a broken axis or inset chart as alternatives to log scale
- Symlog scale (symmetric log) handles data that includes zero — use when log is needed but zeros exist

## Color Beyond the 7-Color Palette

- When categories exceed 7 colors, group the smallest categories into "Other" to stay within palette limits
- Use intensity gradients (light-to-dark of one hue) for ordered categories like severity levels
- Use faceting to split by a secondary dimension instead of adding more colors
- For categorical data >10 groups, consider a bar chart sorted by value instead of a multi-color plot
- When two dimensions need color, use hue for one and pattern/marker shape for the other
- Reserve red for negative/alert and green for positive/success — do not use them as arbitrary category colors
- Test all color choices with a colorblind simulator before finalizing
- When using sequential color scales for numeric data, choose perceptually uniform palettes (viridis, plasma) over rainbow
- For diverging data (positive/negative, above/below average), use diverging color scales centered on the midpoint
