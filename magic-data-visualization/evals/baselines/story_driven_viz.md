# Baseline: Story-Driven Visualization

## Minimum Passing Behavior

A competent agent given the `magic-data-visualization` SKILL.md should:

1. **Story identification first**: Before generating any chart, the agent should articulate what story it wants to tell. The Thinking section asks "What story does the data tell?" as the first question. Expected stories include:
   - "Does income predict satisfaction?" (scatter: income vs satisfaction)
   - "How has satisfaction changed over time?" (line: year vs satisfaction)
   - "Do different regions have different satisfaction?" (bar: region vs satisfaction)
   - "Does transit type affect satisfaction?" (bar: transit_type vs satisfaction)

2. **Chart type matches story**:
   - Scatter plot for income vs satisfaction (two numeric columns, relationship story)
   - Line chart for satisfaction over time (datetime x-axis, trend story)
   - Bar chart for satisfaction by region (categorical comparison, 6 categories)
   - Bar chart for satisfaction by transit type (categorical comparison, 4 categories)

3. **Handling 35 cities**: The 35-city column exceeds the 20-category readability limit stated in the Rules. The agent must aggregate: group by region, use top-10/bottom-10, or filter. Plotting 35 bars raw is a failure.

4. **Descriptive titles**: Titles should convey the insight, not just the chart type. "Higher Income Cities Report Greater Satisfaction" is better than "Scatter Plot: median_income vs satisfaction_score."

5. **Faceted comparison**: When comparing across regions (6 categories), the agent should consider small multiples (faceted panels) rather than cramming everything into one chart.

6. **All anti-patterns avoided**: No pie charts, no 3D, no dual Y-axes, no truncated bar Y-axes. The dataset has enough complexity to tempt several of these.

## Expected Analytical Flow

```
1. Examine data → identify column types and relationships
2. Formulate 3-4 story questions
3. For each story:
   a. Select chart type based on the story-to-chart rules
   b. Choose appropriate columns
   c. Handle high-cardinality columns (cities)
   d. Generate chart with proper formatting
   e. Write insight-driven title
4. Save all charts with descriptive filenames
```

## Expected Charts (minimum 3)

| Story | Chart Type | X | Y | Notes |
|-------|-----------|---|---|-------|
| Income vs satisfaction | Scatter | median_income | satisfaction_score | Color by region optional |
| Satisfaction over time | Line | survey_year | satisfaction_score | Group by region or overall |
| Regional comparison | Bar | region | satisfaction_score | 6 categories, well within limit |

## Failure Indicators

- Generates charts without first identifying the data story
- Plots all 35 cities as individual bars without aggregation
- Uses pie chart for any comparison
- Uses dual Y-axes to overlay income and satisfaction
- Chart titles are generic ("Bar Chart", "Scatter Plot") instead of insight-driven
- Truncates bar chart Y-axis
- Uses default colors instead of colorblind-safe palette
- Generates only one chart when the data supports multiple stories
