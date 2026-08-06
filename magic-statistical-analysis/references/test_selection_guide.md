# Statistical Test Selection Guide

## Decision Tree

```
What are you comparing?
│
├─ Two groups on a numeric variable
│   ├─ Data normal (Shapiro-Wilk p > 0.05)?
│   │   ├─ Yes, equal variance (Levene p > 0.05)? → Independent t-test
│   │   └─ Yes, unequal variance? → Welch's t-test
│   └─ No, non-normal? → Mann-Whitney U test
│
├─ Three or more groups on a numeric variable
│   ├─ Data normal? → One-way ANOVA
│   │   └─ Significant? → Post-hoc: Tukey HSD
│   └─ Non-normal? → Kruskal-Wallis test
│       └─ Significant? → Post-hoc: Dunn's test
│
├─ Two categorical variables
│   └─ Expected counts > 5 in all cells? → Chi-square test
│       └─ Any expected count < 5? → Fisher's exact test (if 2x2)
│
├─ Relationship between two numeric variables
│   ├─ Both normal? → Pearson correlation
│   └─ Either non-normal? → Spearman correlation
│
└─ Before/after on same subjects
    ├─ Normal differences? → Paired t-test
    └─ Non-normal? → Wilcoxon signed-rank test
```

## Test Details

| Test | When | Assumptions | Effect Size |
|------|------|-------------|-------------|
| Independent t-test | 2 groups, normal, equal var | Normality, equal variance | Cohen's d |
| Welch's t-test | 2 groups, normal, unequal var | Normality | Cohen's d |
| Mann-Whitney U | 2 groups, non-normal | Similar shape distributions | Rank-biserial r |
| One-way ANOVA | 3+ groups, normal | Normality, equal variance | Eta-squared (η²) |
| Kruskal-Wallis | 3+ groups, non-normal | Similar shape distributions | Epsilon-squared (ε²) |
| Chi-square | 2 categorical | Expected counts ≥ 5 | Cramér's V |
| Pearson r | 2 numeric, normal | Linearity, normality | r itself |
| Spearman ρ | 2 numeric, any | Monotonic relationship | ρ itself |

## Effect Size Interpretation

### Cohen's d
| Value | Interpretation |
|-------|---------------|
| < 0.2 | Negligible |
| 0.2 - 0.5 | Small |
| 0.5 - 0.8 | Medium |
| > 0.8 | Large |

### Eta-squared (η²)
| Value | Interpretation |
|-------|---------------|
| < 0.01 | Negligible |
| 0.01 - 0.06 | Small |
| 0.06 - 0.14 | Medium |
| > 0.14 | Large |

### Cramér's V
| Value | Interpretation |
|-------|---------------|
| < 0.1 | Negligible |
| 0.1 - 0.3 | Small |
| 0.3 - 0.5 | Medium |
| > 0.5 | Large |

## Common Mistakes

1. **Using t-test on non-normal data with small n:** Use Mann-Whitney instead
2. **Not checking equal variance:** Use Welch's t-test as default (more robust)
3. **Multiple comparisons without correction:** Use Bonferroni or Holm correction
4. **Reporting only p-value:** Always include effect size and confidence interval
5. **Using "significant" without context:** A tiny effect can be "significant" with large n
