# Eval: Multi-Group Comparison

## Task

You have a CSV file at `data/treatment_outcomes.csv` containing clinical trial data. The file has 800 rows and columns: patient_id, treatment_group (placebo, drug_A, drug_B, drug_C), age, outcome_score, side_effects_count. Compare outcome_score across all four treatment groups. Then run pairwise comparisons between each drug and placebo. Report all findings with appropriate corrections for multiple comparisons.

## Context

- This is a multi-group comparison (4 groups: placebo, drug_A, drug_B, drug_C)
- The outcome_score is continuous
- You need an omnibus test first (ANOVA or Kruskal-Wallis), then pairwise follow-ups
- There are 3 pairwise comparisons (each drug vs placebo), so multiple comparison correction is needed
- Clinical data demands careful attention to practical significance, not just statistical significance
- Group sizes may be unequal (the trial may have enrolled more patients in certain arms)

## Expected Behaviors (for scoring)

- [ ] Agent checks normality across all four groups before selecting omnibus test
- [ ] Agent selects ANOVA (if normal) or Kruskal-Wallis (if not) for the omnibus comparison
- [ ] Agent reports omnibus effect size (eta-squared or epsilon-squared)
- [ ] Agent performs pairwise follow-up tests only if omnibus test is significant
- [ ] Agent applies Bonferroni correction (alpha/3) for the 3 pairwise comparisons
- [ ] Agent reports effect size for each pairwise comparison
- [ ] Agent flags any result where p < 0.05 but effect size is negligible as "statistically significant but practically negligible"
- [ ] Agent uses uncertainty language and includes caveats about sample size and assumptions
