# Eval: Basic Summary Report

## Task

You have a findings JSON file at `output/findings.json` from a completed sales analysis. The findings contain:
- Data source: `data/sales_q4.csv`, 2,500 rows, 6 columns
- 3 key findings about quarterly sales trends
- Suggested next steps
- No charts or visualizations

Generate a standard Markdown report at `output/report.md` with all mandatory sections.

## Context

- The audience is a mixed team (data analysts + business stakeholders)
- The `standard` template is appropriate
- No historical baseline data is available for comparison
- The analysis used basic descriptive statistics (mean, median, distribution)

## Findings JSON Structure

```json
{
  "title": "Q4 Sales Analysis",
  "data_source": {"file": "data/sales_q4.csv", "rows": 2500, "columns": 6},
  "summary": "Q4 sales totaled $2.3M across 3 regions.",
  "key_findings": [
    {"title": "Regional Disparity", "description": "West region accounts for 52% of total revenue.", "evidence": "West: $1.2M, East: $0.7M, Central: $0.4M"},
    {"title": "Product Concentration", "description": "Top 3 products generate 78% of revenue.", "evidence": "SKU-A: 35%, SKU-B: 25%, SKU-C: 18%"},
    {"title": "Late Quarter Surge", "description": "December sales were 40% higher than October.", "evidence": "Oct: $0.6M, Nov: $0.8M, Dec: $0.9M"}
  ],
  "methodology": "Descriptive statistics computed on cleaned dataset. Revenue aggregated by region and product.",
  "caveats": ["Analysis is limited to Q4 data only. Year-over-year trends not assessed."],
  "next_steps": ["Compare with Q3 data to identify seasonal patterns.", "Investigate West region driver."]
}
```

## Expected Behaviors (for scoring)

- [ ] Agent generates a report with all 6 mandatory sections: Summary, Data Provenance, Methodology, Key Findings, Caveats, Next Steps
- [ ] Agent leads the summary with the key finding (not methodology)
- [ ] Agent includes at least one caveat (does not skip Caveats section)
- [ ] Agent uses uncertainty language ("suggests", "appears to") rather than certainty language ("proves", "definitively")
- [ ] Agent notes the absence of historical baseline when presenting metrics
- [ ] Agent saves the report as a checkpoint file
