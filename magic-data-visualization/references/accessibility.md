# Accessibility Guidelines for Data Visualization

## Colorblind Safety

### Types of Color Vision Deficiency

| Type | Prevalence | Confuses |
|------|-----------|----------|
| Deuteranopia | 6% of males | Red-green |
| Protanopia | 2% of males | Red-green |
| Tritanopia | 0.01% | Blue-yellow |

### Safe Color Palette

Use the Wong palette (included in our default):
```
#0072B2 (Blue), #E69F00 (Orange), #009E73 (Green),
#CC79A7 (Pink), #56B4E9 (Light blue), #D55E00 (Red-orange), #F0E442 (Yellow)
```

### Rules

1. **Never rely on color alone** — use shape, pattern, or labels as well
2. **Maximum 7 colors** in a single chart
3. **High contrast** between adjacent elements (minimum 4.5:1 ratio)
4. **Use patterns** for fills in bar charts when printed in B&W
5. **Label directly** on the chart when possible (avoid color-only legends)

## Text Accessibility

- Minimum font size: 10pt for screen, 8pt for print
- Use sans-serif fonts (Arial, Helvetica) for readability
- Avoid italics in small sizes
- Use bold sparingly for emphasis

## Alt Text for Charts

When charts are embedded in reports, provide descriptive alt text:

**Template:**
"[Chart type] showing [what is displayed]. [Key observation]. [Number of data points/groups]."

**Example:**
"Bar chart showing revenue by region. North America leads with $2.4M, followed by Europe at $1.8M. 5 regions compared."

## Screen Reader Considerations

- Provide data tables alongside charts for screen readers
- Use structured headings in reports
- Describe trends in text, don't rely solely on visual

## Print Considerations

- Charts should be readable in grayscale
- Use distinct markers/patterns alongside color
- Ensure sufficient contrast at 300 DPI
