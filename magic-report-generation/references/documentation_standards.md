# Documentation Standards for Data Analysis Reports

## Report Structure

Every report MUST contain these sections in order:

1. **Summary** (2-3 sentences)
2. **Data Provenance** (source, size, processing steps)
3. **Methodology** (analyses, tools, assumptions)
4. **Key Findings** (numbered, with evidence)
5. **Caveats and Limitations** (never empty)
6. **Next Steps** (actionable recommendations)

## Writing Style

### Uncertainty Language (Mandatory)

| Instead of | Write |
|-----------|-------|
| "This proves..." | "The data suggests..." |
| "Definitely shows..." | "This appears to indicate..." |
| "X causes Y" | "X appears to be associated with Y" |
| "Significant result" | "Statistically significant (p=0.03, d=0.45)" |
| "Always/never" | "In most cases..." / "Rarely..." |

### Findings Format

Each finding should follow this pattern:
1. **Statement** with uncertainty language
2. **Evidence** with specific numbers
3. **Context** for interpretation
4. **Caveat** or limitation

**Example:**
> **1. Revenue appears right-skewed with potential outliers**
> The median revenue ($5,200) is substantially lower than the mean ($12,400), suggesting a right-skewed distribution (skewness = 2.3). Five accounts exceed $100K, which may be enterprise clients or data entry errors. These outliers influence the mean but not the median, suggesting median is a more representative measure of typical revenue.

## Data Provenance Requirements

| Field | Required | Example |
|-------|----------|---------|
| Source file | Yes | `sales_2024.csv` |
| Row count | Yes | 10,000 rows |
| Column count | Yes | 12 columns |
| Date range | If applicable | Jan 2024 - Dec 2024 |
| Processing steps | Yes | "Loaded → Cleaned (320 nulls imputed) → Validated" |
| Missing data | If any | "3.2% overall (income: 8.2%)" |

## Table Formatting

- Maximum 20 rows displayed (truncate with "... and X more rows")
- Maximum 10 columns displayed
- Numeric formatting: 2 decimals for currency, 4 for statistics
- Cell content: truncate at 50 characters
- Thousands separators for large numbers

## Chart Embedding

```markdown
![Caption describing the chart](path/to/chart.png)

*Figure 1: Revenue distribution shows right skew with 5 outliers above $100K*
```

## Caveats Section (Never Empty)

Even if data appears clean, include at minimum:
- "Analysis is limited to the provided dataset"
- "Results may not generalize beyond this sample"
- "Correlation does not imply causation" (if correlations reported)
