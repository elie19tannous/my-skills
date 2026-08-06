# Baseline: Basic Summary Report

## Minimum Acceptable Behavior

An agent WITHOUT the report-generation skill would typically:
- Dump findings as a flat list or bullet points with no section structure
- Not include Data Provenance or Methodology sections
- Not include Caveats -- present findings as if they are certain
- Use certainty language ("The West region dominates revenue")
- Not note the absence of historical baseline for comparison
- Not save as a checkpoint

## With-Skill Expected Improvements

An agent WITH the report-generation skill should:
1. **All 6 mandatory sections** -- Summary, Data Provenance, Methodology, Key Findings, Caveats, Next Steps are all present with clear section headers
2. **Lead with key finding** -- the summary paragraph opens with the most impactful finding (e.g., "West region accounts for 52% of total revenue"), not with methodology or data description
3. **Uncertainty language** -- uses "suggests", "appears to", "may indicate" rather than "proves" or "definitively shows"
4. **Baseline awareness** -- explicitly notes that no historical baseline is available for year-over-year comparison, rather than presenting Q4 numbers in isolation
5. **Caveats present** -- includes at least the caveat about Q4-only data and lack of year-over-year trends
6. **Checkpoint saved** -- output is saved as a report file with a descriptive name

## Key Differentiators

The skill prevents the two most common report failures: (1) missing sections that destroy trust (no Caveats section makes stakeholders think you didn't consider limitations), and (2) presenting numbers without baseline context (readers cannot assess whether "52% of revenue from West" is good, bad, or expected without comparison).
