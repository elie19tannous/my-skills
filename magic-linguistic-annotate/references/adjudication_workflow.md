# Adjudication Workflow — Reference

Loaded by `magic-linguistic-annotate` Step 4.

## Why adjudication matters

Without adjudication, multi-annotator outputs are inconsistent. Two annotators disagree → which label wins? Without curator pass, you ship inconsistent gold. Inconsistent gold = noisy training signal + unreliable eval.

Adjudication = curator (senior annotator or domain expert) reviews disagreements and produces a final canonical label.

## When to adjudicate

- All items where annotators disagree.
- 10-20% sample of items where annotators agree (catches systematic agreement on wrong labels).
- New edge cases that emerge during bulk.

## Curator role

- Reviews disagreements + agreement-sample audit.
- Picks resolution (or "ambiguous — exclude" tag).
- Updates guidelines when a new pattern emerges.
- Tracks per-annotator disagreement rates.

Single curator is OK for medium projects. Large/critical: use 2 curators with their own IAA + meta-curator.

## Adjudication decision categories

| Category | Action |
|---|---|
| Annotator A correct | Final label = A |
| Annotator B correct | Final label = B |
| Both wrong; clear correct answer | Final label = curator's choice |
| Genuinely ambiguous | Tag as "ambiguous"; exclude from gold OR include with low confidence |
| Guideline gap | Update guideline + add to edge-case log + apply to similar items |

## Per-annotator quality tracking

Compute per-annotator agreement vs the adjudicated final:
- **Annotator A vs final:** 92% agreement → annotator A is reliable.
- **Annotator B vs final:** 75% agreement → annotator B needs retraining or guideline reinforcement.

Track these. Use to prioritize calibration sessions, identify systematic bias, decide whether to retrain or replace.

## Adjudication rate as a guideline-quality signal

| Adjudication rate (% items disagreed) | Meaning |
|---|---|
| < 5% | Guideline very clear; annotators well-calibrated |
| 5-15% | Normal; healthy edge-case discovery |
| 15-30% | Guideline ambiguity; revise + recalibrate |
| > 30% | Severe issue: task or guidelines fundamentally broken; pause bulk |

## Edge-case log: the canonical artifact

Every adjudicated decision should be logged. Format:

```markdown
## Edge case: <date> — <short title>
**Item:** <copy of disputed item>
**Annotator A label:** X
**Annotator B label:** Y
**Curator decision:** Z
**Rationale:** ...
**Guideline update:** [Yes - section X.Y / No - already covered]
**Similar items:** N already-annotated to revisit
```

The log is the durable knowledge. Annotators graduate to curators by reading the log.

## Re-annotation when adjudication reveals systemic issue

If curator finds 20% of bulk has a systematic mistake (e.g., misunderstood label X = label Y), you must re-annotate. Cost is 100× the original calibration cost. This is why calibration matters.

## Common adjudication failures

- **Curator picks "majority" without thinking:** if both annotators are wrong in the same way, "majority" is wrong gold.
- **Curator picks own preference rather than what guideline says:** drift opposite direction.
- **Curator decisions not logged:** future annotators repeat the disagreement.
- **Curator overworked:** quality drops; consider 2 curators with cross-check.
- **No timeline for adjudication:** curator queues build up; annotators forget context.

## Tools

- Most annotation platforms (Label Studio, Prodigy, INCEpTION) have built-in adjudication views.
- For curator-vs-annotator IAA, recompute κ using curator-decisions as one rater.

## See also

- **Pustejovsky, J., & Stubbs, A.** (2012). *Natural Language Annotation for Machine Learning*. O'Reilly.
- **Hovy, D., et al.** (2014). *Learning Whom to Trust with MACE* (annotator quality modeling). NAACL.
- **Carpenter, B.** (2008). *Multilevel Bayesian Models of Categorical Data Annotation*. Tech report.
