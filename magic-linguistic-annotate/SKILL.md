---
name: magic-linguistic-annotate
description: 'Design, run, and audit annotation projects: guideline authoring methodology, IAA (inter-annotator agreement) metric selection (Cohen κ, Fleiss κ, Krippendorff α, γ), adjudication workflow, active learning for sample selection. Use whenever the user mentions annotation, labeling, gold standard, IAA, kappa, alpha, Krippendorff, Fleiss, agreement, adjudication, active learning, annotator disagreement, calibration round, guideline drift, Label Studio, Prodigy, Doccano, INCEpTION, brat, or asks how to build a labeled dataset for [language]. **Use BEFORE starting bulk annotation** — guideline design + calibration costs less than re-annotating 20% of bulk later. Routed by magic-linguistic-orchestrator in the Analyze phase whenever new gold-standard data is being created.'
license: Apache-2.0
compatibility: Python 3.12+
metadata:
  domain: linguistics
  complexity: medium
  requires_llm: false
  phase: 3
  supports_pipeline: true
  supports_generation: false
  entry_point: false
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - linguistics
  - annotation
  - iaa
  - gold-standard
  - low-resource
  dependencies: []
  scripts:
  - scripts/annotation_plan_advisor.py
  - scripts/iaa_calculator.py
---

## When to Use

- Designing a new annotation project (NER, POS, parsing, sentiment, MT eval, anything).
- Selecting an IAA metric for the task.
- Calculating IAA from given counts.
- Running adjudication after multi-annotator pass.
- Active-learning sample selection for limited annotation budget.
- Deciding whether to ship a single-annotator gold dataset (usually NO).

**When NOT to use:** purely synthetic-data generation → no human labels needed. Adapter / training itself → `magic-linguistic-transfer`. Existing gold-standard reuse without modification → just use it.

## The Knowledge Engineers Routinely Miss

1. **Cohen κ is misleading on highly skewed classes.** When 90% of items are "negative" and annotators agree on most by chance, κ underestimates real agreement. Use PABAK (Prevalence-Adjusted Bias-Adjusted κ) or report F1-complement.

2. **Krippendorff α handles missing data + ordinal scales** that κ doesn't. For serious projects with > 2 annotators, partial-coverage data, or ordinal labels (Likert): default α.

3. **γ (gamma) is for span/unitized tasks** (NER spans, coreference chains, discourse units). Don't use κ for spans — it doesn't model span boundaries.

4. **κ ≥ 0.8 = "good"; 0.67-0.8 = "tentative"** but report **CIs**. A single number agreement on small sample is unreliable. Bootstrap CI is standard.

5. **Adjudication is REQUIRED**, not optional. Without curator pass on disagreements, annotator-level guideline drift accumulates and the gold drifts from the spec.

6. **Calibration rounds are non-negotiable.** 50-100 items annotated by ALL annotators with discussion BEFORE bulk. Skipping calibration → 10-20% of bulk needs re-annotation. The cost asymmetry is brutal.

7. **Active learning is uncertainty > random** for most tasks; **clustering-based > uncertainty** for very-low-resource where you want diverse coverage. The default "uncertainty sampling" advice fails when target distribution is itself sparse.

8. **Single-annotator gold = no gold.** A label without IAA evidence is opinion, not data. The exception: a recognized expert + a stated subjectivity disclaimer.

## Workflow

### Step 1 — Define the annotation task

**MANDATORY READ** [`references/guideline_authoring.md`](references/guideline_authoring.md).

- What is the unit (token / span / sentence / document)?
- What are the labels (closed set / open / hierarchical)?
- What's the boundary policy (where does a span start/end)?
- What's the tie-breaker rule for ambiguous cases?
- What edge cases must be documented?

### Step 2 — Author guidelines (draft → pilot → calibration → bulk)

Iterative loop:
1. **Draft v0**: based on task definition + 20-30 example items.
2. **Pilot**: 50 items annotated by 2-3 annotators independently; discuss disagreements; revise guidelines.
3. **Calibration**: 100 items, all annotators, with per-decision discussion. Update edge-case log.
4. **Bulk**: full corpus; 10% double-annotated for IAA monitoring.
5. **Adjudication**: curator resolves all disagreements.

Skipping any step = downstream cost.

### Step 3 — Select IAA metric

**MANDATORY READ** [`references/iaa_metrics.md`](references/iaa_metrics.md).

Use `scripts/iaa_calculator.py`:

| Task type | # annotators | Metric | Why |
|---|---|---|---|
| Binary / nominal categorical | 2 | Cohen κ | Standard; reports chance-adjusted agreement |
| Same, skewed prevalence | 2 | PABAK or F1-complement | κ misleads on imbalance |
| Same, ≥ 3 annotators | ≥ 3 | Fleiss κ | Multi-annotator κ |
| Ordinal labels (Likert, severity) | any | Krippendorff α (ordinal) | κ doesn't handle ordinal |
| Missing values per annotator | any | Krippendorff α | Handles missingness |
| Span / unitized (NER, coref) | any | γ (gamma) | Models boundaries |
| Free-text overlap | any | F1 / BLEU / ROUGE | No κ-style metric for unconstrained text |

**Threshold convention**: ≥ 0.8 "good"; 0.67-0.8 "tentative"; < 0.67 unreliable. Always report **bootstrap CI**.

### Step 4 — Adjudication workflow

**MANDATORY READ** [`references/adjudication_workflow.md`](references/adjudication_workflow.md).

For each item where annotators disagree:
1. Curator (senior annotator or domain expert) reviews.
2. Curator picks resolution OR defers to "ambiguous — exclude" tag.
3. Curator updates guidelines if a new edge-case pattern emerges.
4. Track per-annotator disagreement rates — high rates indicate annotator drift, training gap, or guideline ambiguity.

### Step 5 — Active learning (when annotation budget is limited)

**MANDATORY READ** [`references/active_learning.md`](references/active_learning.md).

Use `scripts/annotation_plan_advisor.py`:

| Approach | Best for | Tradeoff |
|---|---|---|
| Random sampling | Baseline | Simplest; under-samples rare |
| Uncertainty sampling (model-based) | Most cases | Catches uncertain examples; bias toward model blind spots |
| Diversity (cluster-based) | Very low resource | Best coverage of distribution; less sensitive to model |
| Hybrid (uncertainty + diversity) | Production | Strongest in practice |

Recommend ≥ 100 calibration items + active-loop batches of 100-500.

### Step 6 — Output annotation plan + hand off

```markdown
## Annotation Plan: <Task>

**Unit:** token / span / sentence / document
**Labels:** ...
**Annotators:** N (recommend ≥ 2 with curator)
**Calibration round size:** 100 items (mandatory)
**IAA metric:** Cohen κ | Fleiss κ | Krippendorff α | γ — rationale: ...
**Threshold to ship:** κ ≥ 0.8 (or specified)
**Adjudication owner:** ...
**Active learning:** uncertainty | diversity | hybrid | random
**Hand-off:** magic-linguistic-eval (gold for benchmark); magic-linguistic-syntax/morph/etc. (gold for analysis)
```

## Anti-patterns (NEVER do)

- **NEVER** use Cohen κ on highly skewed classes (use PABAK or F1-complement).
- **NEVER** ship single-annotator gold without an explicit subjectivity disclaimer.
- **NEVER** skip calibration rounds. 10-20% bulk re-annotation cost dwarfs the day spent calibrating.
- **NEVER** report aggregate IAA across heterogeneous tasks. Per-task IAA only.
- **NEVER** report κ without bootstrap CI when sample < 200.
- **NEVER** use κ for span tasks (NER, coreference). Use γ.
- **NEVER** treat curator decisions as un-auditable. Curator decisions get logged + reviewable.
- **NEVER** skip the edge-case log. Every adjudication decision is potential guideline material.

## Edge Cases

- **Single expert annotator with deep domain knowledge** (e.g., named-entity gold for an obscure historical text): document subjectivity; offer to validate with second annotator if budget permits.
- **Crowd-source platform** (MTurk, Prolific): per-worker quality gating; reject below per-task κ ≥ 0.6 with majority vote.
- **Annotators disagree systematically** (one annotator strict, one lenient): bias-adjusted IAA reveals it; calibration discussion required.
- **Task has subjective component** (sentiment, hate speech): expect lower κ (~0.6-0.7); use Krippendorff α; report explicitly as subjective.
- **Cross-language annotation** (annotator + curator different language native): native-speaker required for at least one; document.
- **Active learning dataset shift** (model gets better; old "uncertain" examples now easy): re-pool periodically.
- **Annotation tool crash mid-project**: per-item save; commit annotations every batch.

## Output Format

```markdown
## Annotation Project: <Task>

**Stage:** draft / pilot / calibration / bulk / adjudication / shipped
**Unit + labels:** ...
**Annotators:** N (per-annotator productivity tracked)
**IAA metric:** ... (with chosen threshold + bootstrap CI)
**Calibration result:** κ = X (95% CI [a,b])
**Pilot result:** κ = X
**Bulk IAA (10% sample):** κ = X
**Adjudication: % disagreements / total items:** X%
**Edge cases logged:** N (link)
**Active-learning: round / batch / total annotated:** ...
**Anti-patterns avoided:** ...
**Hand-off:** ...
```
