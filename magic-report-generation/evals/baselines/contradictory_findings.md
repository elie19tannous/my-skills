# Baseline: Contradictory Findings

## Minimum Acceptable Behavior

An agent WITHOUT the report-generation skill would typically:
- Cherry-pick the statistically significant result (mean-based, p=0.003) and present it as the conclusion: "The campaign increased revenue by 22%"
- Bury or omit the median-based finding entirely, or mention it as a footnote
- Provide a definitive "yes/no" answer to "did the campaign work?"
- Not explain the outlier dynamics driving the discrepancy
- Not frame the contradiction as a distributional measurement question

## With-Skill Expected Improvements

An agent WITH the report-generation skill should:
1. **Present both findings prominently** -- both the mean-based increase (22%, p=0.003) and the median-based decrease (3%, p=0.12) appear as primary findings, not one primary and one buried
2. **Explain the contradiction** -- the outlier concentration (top 2% = 35% of revenue) is presented as the explanatory mechanism, not just a curiosity
3. **No false resolution** -- does not declare one analysis "correct" and the other "wrong"; frames both as measuring different distributional aspects
4. **Distributional framing** -- explains that mean captures total revenue impact (including tail), median captures typical customer experience, and both are valid lenses
5. **Statistical rigor** -- includes p-values, effect sizes (Cohen's d, rank-biserial r), and trimmed mean as a robustness check
6. **Nuanced conclusion** -- acknowledges that "did the campaign work?" depends on what you mean: it generated revenue through a small high-value segment, but did not change behavior for the majority
7. **Actionable next steps** -- proposes segment analysis and extended measurement as paths to resolve the ambiguity, rather than re-running the same analyses

## Key Differentiators

The skill prevents the most dangerous report failure: cherry-picking results that support a desired narrative. Without the skill, agents default to reporting the statistically significant finding as "the answer" and treating the non-significant finding as noise. The skill teaches that contradictory findings from valid methods are information, not error -- they reveal distributional complexity that a single summary statistic hides. This is the hardest eval because it requires the agent to resist the pull toward a clean narrative and instead present honest complexity.
