# Data Storytelling Patterns Reference

Patterns for turning analysis results into clear, audience-appropriate narratives.

## Structural Patterns

Apply these rules when composing any data analysis report:

1. **Lead with "so what"**: Open every section with the implication, not the method.
   Write "Revenue dropped 12% in Q3 driven by churn in Segment A" before explaining how you measured it.
2. **One finding per visualization**: Never overload a single chart with multiple conclusions.
   If a chart supports two findings, present it twice with different annotations or split into two charts.
3. **Compare to a baseline**: Raw numbers lack context. Always pair a metric with its comparison
   point -- prior period, target, industry benchmark, or population average.
4. **Quantify uncertainty**: When a finding depends on sample size, imputation, or assumptions,
   state the confidence range. Write "likely between 8-14% (based on 200 observations)" not just "about 11%".
5. **Separate facts from interpretation**: Use distinct sections or visual cues.
   Facts: "Column X has 23% nulls." Interpretation: "This suggests upstream data collection issues in Region B."

## Audience Adaptation

| Audience | Structure | Language | Detail Level |
|---|---|---|---|
| Technical (analysts, engineers) | Method-first; include code references and assumptions; link to notebooks | Use precise statistical terms; include p-values, confidence intervals | Full detail; include edge cases, data quality notes, and caveats |
| Executive (directors, C-suite) | Conclusion-first; one-page summary up front; appendix for detail | Plain language; replace jargon with impact statements ("saves $X" not "reduces variance") | High-level only; 3-5 key findings; defer methodology to appendix |
| Mixed (cross-functional teams) | Layered: executive summary then progressive detail sections | Define terms on first use; use analogies for statistical concepts | Start broad, let readers self-select depth; use collapsible sections if format allows |

### Audience Detection Cues

- "for my team" / "for standup" -- assume technical. "for leadership" / "for the board" -- assume executive.
- "share with stakeholders" or unspecified -- assume mixed. When uncertain, default to mixed.

## Report Structure Decision Guide

| Scenario | Recommended Structure | Key Sections |
|---|---|---|
| Single analysis | Linear narrative: context, method, findings, implications | Background, Approach, Key Findings (ranked), Recommendations, Caveats |
| Multiple analyses | Thematic grouping with shared executive summary | Executive Summary, then one section per theme, each with own findings and evidence |
| Comparison (A vs B) | Side-by-side with explicit dimensions of comparison | Comparison Framework, Dimension-by-Dimension Results, Overall Assessment, Recommendation |
| Incremental update | Delta-focused: what changed since last report | Changes Since Last Report, Updated Metrics, New Findings, Revised Recommendations |
| Contradictory findings | Tension-first: name the contradiction, then resolve or explain | The Contradiction, Evidence For A, Evidence For B, Reconciliation / Remaining Uncertainty |

When in doubt, count distinct questions the report answers -- two or more means multiple-analyses.
Use incremental update only when a prior report exists. Use contradictory-findings when you are hedging.

## Finding Presentation Hierarchy

Present findings in this priority order -- readers remember what comes first:

1. **Actionable findings** (highest priority): Results that directly suggest a decision or intervention.
   Example: "Segment C has 3x higher churn -- targeted retention offers are warranted."
2. **Surprising findings**: Results that contradict assumptions or prior beliefs.
   Example: "Despite higher spend, Campaign B underperformed Campaign A on conversion."
3. **Confirming findings**: Results that validate existing hypotheses. Keep these brief.
   Example: "As expected, weekend traffic is 40% lower than weekday traffic."
4. **Informational findings** (lowest priority): Descriptive statistics and context that frame the analysis.
   Example: "The dataset contains 1.2M rows spanning Jan 2023 to Dec 2025."

### Applying the Hierarchy

- When a report has 10+ findings, group by priority tier and present tiers in order.
- When a report has fewer than 5 findings, order them directly by the hierarchy.
- Always flag which tier a finding belongs to so readers can triage their attention.
- If no findings are actionable, say so explicitly -- do not manufacture false urgency.
- When two findings share the same tier, order by magnitude of impact, then by confidence level.
