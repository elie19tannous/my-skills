# IAA Metrics — Reference

Loaded by `magic-linguistic-annotate` Step 3.

## The four main metrics

| Metric | When | Range | What it measures |
|---|---|---|---|
| **Cohen κ** | 2 annotators, nominal | -1 to 1 | Agreement above chance |
| **Fleiss κ** | ≥ 3 annotators, nominal | -1 to 1 | Same, generalized to N annotators |
| **Krippendorff α** | Any N annotators, nominal/ordinal/missing data | -1 to 1 | Disagreement-based; handles partial annotation |
| **γ (gamma)** | Span/unitized tasks (NER, coref, discourse) | 0 to 1 | Span boundaries + label agreement |

## Threshold convention (Landis & Koch 1977)

| κ / α | Interpretation |
|---|---|
| < 0 | Worse than chance |
| 0.0 - 0.20 | Slight |
| 0.21 - 0.40 | Fair |
| 0.41 - 0.60 | Moderate |
| 0.61 - 0.80 | Substantial / "tentative" |
| 0.81 - 1.00 | "Almost perfect" / "good" |

Practical: aim for ≥ 0.8 to ship. 0.67-0.8 = note as tentative. < 0.67 = guideline rework.

**Always report bootstrap CI** when N < 200. Single-number IAA on small sample is unreliable.

## Cohen κ — common pitfalls

- **Skewed prevalence kills κ.** If 95% of items are class A and 2 annotators agree on 98% of items by mostly agreeing on class A, κ can be ≤ 0.5 even though "real agreement" is 0.98. → Use PABAK or F1-complement.
- **Bias** between annotators (one always picks A, other always picks B for ambiguous): κ shows artificially low; report bias-adjusted variant.

## Krippendorff α — when to use over κ

- More than 2 annotators with possibly missing data.
- Ordinal data (severity, Likert).
- Different distance functions per data type (interval, ratio, polar).

α is more general than κ; preferred for serious annotation projects.

## γ (gamma) — for span/unitized

- NER spans, coreference chains, discourse units.
- Models both span boundary agreement AND label agreement.
- Not interchangeable with κ.

GammaScore implementation: pyAnnote / mAP-Annotation.

## Computing IAA in practice

```python
# Cohen κ (two annotators)
from sklearn.metrics import cohen_kappa_score
kappa = cohen_kappa_score(annotator_a_labels, annotator_b_labels)

# Fleiss κ (≥ 3 annotators)
import statsmodels.stats.inter_rater as ir
kappa = ir.fleiss_kappa(matrix)  # matrix: items × labels (counts)

# Krippendorff α
import krippendorff
alpha = krippendorff.alpha(reliability_data, level_of_measurement='nominal')
# levels: nominal, ordinal, interval, ratio

# γ for spans
# Use pyannote or custom; sklearn doesn't have it
```

## Reporting template

```
Annotation: <task name>
Annotators: N (with curator)
Sample double-annotated: 10% (N items)
IAA metric: <Cohen κ | Fleiss κ | Krippendorff α | γ>
Result: 0.84 (95% bootstrap CI: [0.80, 0.88])
Threshold to ship: ≥ 0.8 — MET / NOT MET
Per-class breakdown: ... (often more revealing than aggregate)
Adjudicated disagreements: N items
Edge cases added to guideline: N
```

## When IAA is "not enough"

For high-stakes annotation (medical, legal, ground-truth eval), supplement IAA with:
- Per-class IAA (some classes are inherently harder).
- Per-annotator quality scoring.
- External validation against published gold (when comparable).
- Adjudication-rate tracking (high adjudication % = something off in guidelines).

## Common reporting failures

- Reporting aggregate κ across heterogeneous task types (POS + sentiment in same number).
- Reporting κ without n (sample size).
- Reporting κ without CI on small N.
- Cherry-picking "agreement %" instead of κ (raw agreement always inflated by chance).
- Comparing κ across tasks with very different label-set sizes.

## See also

- **Artstein, R., & Poesio, M.** (2008). *Inter-Coder Agreement for Computational Linguistics*. Computational Linguistics.
- **Krippendorff, K.** (2018). *Content Analysis: An Introduction to Its Methodology* (4th ed.). Sage.
- **Landis, J. R., & Koch, G. G.** (1977). *The Measurement of Observer Agreement for Categorical Data*. Biometrics.
- **Mathet, Y., Widlöcher, A., Métivier, J.-P.** (2015). *The Unified and Holistic Method Gamma (γ) for Inter-Annotator Agreement Measure and Alignment*. Computational Linguistics.
