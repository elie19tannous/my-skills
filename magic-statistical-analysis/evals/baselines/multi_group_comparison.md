# Baseline: Multi-Group Comparison

## Minimum Acceptable Behavior

An agent WITHOUT the statistical-analysis skill would typically:
- Run multiple t-tests between each pair of groups without correction
- Not perform an omnibus test (ANOVA/Kruskal-Wallis) first
- Not check normality before selecting parametric tests
- Not apply multiple comparison correction (Bonferroni or FDR)
- Report raw p-values without effect sizes
- Not distinguish between statistical and practical significance

## With-Skill Expected Improvements

An agent WITH the statistical-analysis skill should:
1. **Omnibus test first** — run ANOVA or Kruskal-Wallis across all four groups before pairwise follow-ups; only proceed to pairwise tests if the omnibus test is significant
2. **Normality-based test selection** — check normality in all four groups with Shapiro-Wilk; select ANOVA if all pass, Kruskal-Wallis if any fail
3. **Multiple comparison correction** — apply Bonferroni correction (alpha/3 = 0.0167) to the three pairwise comparisons (drug_A vs placebo, drug_B vs placebo, drug_C vs placebo)
4. **Effect size for every comparison** — report eta-squared or epsilon-squared for the omnibus test and Cohen's d or rank-biserial r for each pairwise comparison
5. **Practical significance gating** — flag results where p < adjusted_alpha but effect size is negligible (e.g., d < 0.2) as "statistically significant but practically negligible"
6. **Structured reporting** — present omnibus result first, then conditionally present pairwise results with corrected thresholds

## Key Differentiators

The skill prevents the two most dangerous multi-group mistakes: (1) running pairwise tests without an omnibus test first (inflated Type I error), and (2) running multiple tests without correction (1 in 20 expected false positives per test). Without the skill, an agent running 6 pairwise t-tests at alpha=0.05 has a ~26% chance of at least one false positive. With the skill, the agent follows the correct omnibus-then-pairwise protocol with Bonferroni correction.
