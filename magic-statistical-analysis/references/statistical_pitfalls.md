# Statistical Pitfalls — When to Be Cautious

## P-Hacking and Multiple Comparisons

**Risk:** Testing many hypotheses and reporting only the significant ones.

**When to suspect:** Many variables tested, no pre-registration, only "interesting" results reported.

**Mitigation:** Apply Bonferroni correction (α/n) or Holm-Bonferroni. Report ALL tests run, not just significant ones.

## Small Sample Inflation

**Risk:** Small samples produce unstable estimates with artificially large effect sizes.

**When to suspect:** n < 30 per group, effect sizes seem surprisingly large.

**Mitigation:** Report confidence intervals (which will be wide). Note sample size limitations. Consider power analysis.

## Outlier Sensitivity

**Risk:** A few extreme values can dominate means, correlations, and test results.

**When to suspect:** Mean >> median, or single data points drive the conclusion.

**Mitigation:** Run analysis with and without outliers. Report both results. Use robust methods (median, trimmed mean, rank-based tests).

## Confounding Variables

**Risk:** An unmeasured third variable explains the apparent relationship.

**When to suspect:** Observational (non-experimental) data, relationship seems too strong or surprising.

**Mitigation:** List possible confounders. Use stratification or regression to control for known confounders. Never claim causation.

## Base Rate Neglect

**Risk:** Ignoring the base rate of an event when interpreting conditional probabilities.

**When to suspect:** Reporting precision/recall without base rate, rare events in binary classification.

**Mitigation:** Always report the base rate. Use metrics appropriate for imbalanced data (precision-recall, not just accuracy).

## Regression to the Mean

**Risk:** Extreme values on first measurement tend to be closer to the mean on second measurement, regardless of any intervention.

**When to suspect:** Pre-post comparisons, selecting subjects based on extreme initial values.

**Mitigation:** Use control groups. Acknowledge regression to the mean in caveats.

## Overfitting Narratives

**Risk:** Finding patterns in noise, especially with many features and few observations.

**When to suspect:** p << features, model fits training data perfectly, "discoveries" in small datasets.

**Mitigation:** Use holdout validation. Report the number of features examined. Apply multiple comparison corrections.

## Caveats Checklist

Before reporting any statistical result, verify:
- [ ] Effect size reported alongside p-value
- [ ] Confidence intervals provided
- [ ] Assumptions checked and reported
- [ ] Sample size noted
- [ ] Multiple comparisons addressed
- [ ] Uncertainty language used
- [ ] At least one caveat included
- [ ] Correlation ≠ causation noted (if applicable)
