# Baseline: Multi-Section Report

## Minimum Acceptable Behavior

An agent WITHOUT the report-generation skill would typically:
- Use a generic template regardless of audience -- lead with methodology for executives
- Present "12% churn rate" without comparison to last quarter (8%) or industry average (15%)
- Dump the full 45-row segment summary table without truncation, making the report unreadable
- Present confidence intervals only if explicitly in the findings, not proactively
- Embed charts as raw file paths rather than Markdown image syntax with captions
- Omit or minimize caveats, especially the Midwest sample size limitation

## With-Skill Expected Improvements

An agent WITH the report-generation skill should:
1. **Executive template selection** -- leads with the decision ("Churn rose to 12%, up from 8% last quarter, though still below the 15% industry average") not methodology
2. **Baseline comparison** -- every metric includes context: 12% vs. 8% prior quarter, vs. 15% industry, with explicit labeling of each comparison
3. **Uncertainty quantification** -- includes 95% CI (10.5-13.5%) and sample sizes (N=15,000) for key metrics; notes where sample size limits confidence (Midwest N=1,200)
4. **Table formatting** -- shows top 10 of 45 segments with a truncation note, proper number formatting with thousands separators
5. **Chart embedding** -- uses `![caption](path)` syntax with descriptive captions, not raw paths
6. **Complete caveats** -- includes all three caveats, especially the methodological note about activity-based vs. contract-based churn definition
7. **Facts vs. interpretation** -- "churn increased from 8% to 12%" is labeled as observed fact; "indicates retention crisis" would be labeled as interpretation

## Key Differentiators

The skill teaches audience-appropriate template selection (the single highest-impact decision in report generation) and baseline comparison discipline. Without the skill, agents produce technically correct but unreadable reports for executive audiences -- too much methodology, no comparison context, and raw data tables that obscure the story.
