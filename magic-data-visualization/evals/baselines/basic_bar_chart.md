# Baseline: Basic Bar Chart

## Minimum Passing Behavior

A competent agent given the `magic-data-visualization` SKILL.md should:

1. **Chart type selection**: Recognize that `region` (categorical) vs `total_sales` (numeric) is a comparison story and select a bar chart. This maps directly to the "comparison -> bar" rule in Data Processing Expertise.

2. **Palette**: Use the colorblind-safe palette `['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9', '#D55E00', '#F0E442']` as required by the Constraints section.

3. **Axis labels**: Label both axes with human-readable names ("Region", "Total Sales" or similar), not raw column names like `region` and `total_sales`.

4. **Title**: Include a descriptive title (e.g., "Total Sales by Region" or "Regional Sales Comparison").

5. **Y-axis origin**: Y-axis starts at zero. The Constraints explicitly state "NEVER truncate bar chart Y-axis."

6. **Anti-patterns avoided**: No pie chart, no 3D, no dual Y-axes. These are all listed as NEVER constraints.

7. **Technical quality**: 300 DPI, top/right spines removed, `tight_layout()`.

## Expected Code Pattern

The agent should produce code similar to the "Bar / scatter / line generation" seed pattern, adapted for this specific dataset. Key elements:

```python
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
df.groupby("region")["total_sales"].mean().plot(kind="bar", ax=ax, color="#0072B2")
ax.set_xlabel("Region")
ax.set_ylabel("Total Sales")
ax.set_title("Total Sales by Region")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig("charts/sales_by_region.png", dpi=300, bbox_inches="tight")
```

## Failure Indicators

- Chooses pie chart for this comparison task
- Uses default matplotlib colors instead of colorblind-safe palette
- Missing axis labels or title
- Y-axis does not start at zero
- Uses 3D effects or chart junk
