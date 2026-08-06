# Visualization Style Guide

## Color Palette (Colorblind-Safe)

Primary palette (diverging-friendly, safe for all forms of color blindness):

```python
COLORBLIND_PALETTE = [
    '#0072B2',  # Blue
    '#E69F00',  # Orange
    '#009E73',  # Green
    '#CC79A7',  # Pink
    '#56B4E9',  # Light blue
    '#D55E00',  # Red-orange
    '#F0E442',  # Yellow
]
```

### Sequential Palette (for heatmaps)
- Use `seaborn.color_palette("RdBu_r", as_cmap=True)` for diverging (correlation heatmaps)
- Use `seaborn.color_palette("YlOrRd", as_cmap=True)` for sequential (density)

### Single-Color Variations
For single-series charts, use `#0072B2` (blue) as default.

## Typography

| Element | Size | Weight |
|---------|------|--------|
| Title | 14pt | Bold |
| Axis labels | 12pt | Normal |
| Tick labels | 10pt | Normal |
| Legend | 10pt | Normal |
| Annotations | 9pt | Normal |

## Layout

- **Figure size:** 10×6 inches (landscape) for most charts
- **DPI:** 300 for publication, 150 for screen
- **Margins:** `tight_layout()` always
- **Format:** PNG (default) + SVG (optional vector)

## Matplotlib Style Setup

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_theme(style="whitegrid", palette=COLORBLIND_PALETTE)
plt.rcParams.update({
    'figure.figsize': (10, 6),
    'figure.dpi': 300,
    'font.size': 10,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'legend.fontsize': 10,
    'axes.spines.top': False,
    'axes.spines.right': False,
})
```

## Chart-Specific Guidelines

### Histogram
- 10-30 bins (auto with Sturges or Freedman-Diaconis)
- Add vertical line for mean and/or median
- Label with count or density

### Bar Chart
- Horizontal bars for >5 categories (easier to read labels)
- Sort by value (descending) for ranking
- Start y-axis at 0

### Scatter Plot
- Add transparency (alpha=0.5) for overlapping points
- Add trend line only if correlation is significant
- Use jitter for discrete values

### Line Chart
- Use markers for <20 data points
- No markers for >20 data points
- Fill area below for single series (optional)

### Box Plot
- Show individual outlier points
- Consider violin plot for distribution shape
- Add swarm plot overlay for small datasets
