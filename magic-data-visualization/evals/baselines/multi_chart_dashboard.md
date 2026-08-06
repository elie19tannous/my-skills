# Baseline: Multi-Chart Dashboard

## Minimum Passing Behavior

A competent agent given the `magic-data-visualization` SKILL.md should:

1. **Story-to-chart mapping**:
   - Revenue over time: line chart (trend story, datetime x-axis)
   - Revenue by category: bar chart (comparison story, categorical x-axis)
   - Orders vs avg_order_value: scatter plot (relationship story, two numeric columns)
   - Return rate distribution: histogram (distribution story, single numeric column)

2. **No dual Y-axes**: The task includes both `revenue` and `orders` which could tempt a dual-axis overlay. The agent must use separate charts or small multiples, per the NEVER constraint.

3. **Grouped line chart**: The revenue-over-time chart should use color-coded lines per category (4 categories fits within the 7-color palette). The agent should apply `group_col` or iterate over categories.

4. **Consistent formatting**: All 4 charts should use the same palette, axis formatting conventions, DPI, and spine removal.

5. **Separate files**: Each chart saved to its own file with a descriptive name (e.g., `charts/revenue_trend.png`, `charts/revenue_by_category.png`, `charts/orders_vs_aov.png`, `charts/return_rate_distribution.png`).

## Expected Code Pattern

The agent should produce 4 independent chart blocks. For the line chart:

```python
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
for i, (name, group) in enumerate(df.groupby("category")):
    ax.plot(group["date"], group["revenue"], color=PALETTE[i], label=name, linewidth=2)
ax.legend(title="Category")
ax.set_xlabel("Date")
ax.set_ylabel("Revenue ($)")
ax.set_title("Daily Revenue by Category (2024)")
```

## Failure Indicators

- Uses dual Y-axes to overlay revenue and orders on the same chart
- Uses pie chart for category comparison
- Uses bar chart for the time-series trend
- Uses the same chart type for all 4 visualizations
- Missing axis labels or titles on any chart
- Uses default matplotlib colors instead of the colorblind-safe palette
- Saves all charts to a single file instead of separate files
