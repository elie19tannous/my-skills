# Synthetic Bitext — Reference

Loaded by `magic-linguistic-bitext` Step 5 when real parallel < 100K pairs.

## When to go synthetic

Real parallel sentence count thresholds:
- ≥ 1M pairs: usually no synthetic needed.
- 100K - 1M: optional synthetic to fill gaps.
- 10K - 100K: synthetic recommended.
- < 10K: synthetic essential; expect quality limitations.

## Three main strategies

### 1. Back-translation

**Setup**: train a target → source MT on the limited real parallel.
**Apply**: back-translate target monolingual corpus → produce synthetic source.
**Result**: pairs of (synthetic source, real target) for forward MT training.

**Critical**: temperature matters.
- T=0 (greedy): translationese drift; synthetic source over-mirrors structure of target language.
- T=0.7-1.0 (sampling): diversity; better generalization.
- T > 1.5: noise dominates.

Default: T=0.9 with nucleus sampling (top_p=0.95).

**Tag synthetic pairs** with `<bt>` token at training time so model learns to weight them appropriately. Some configurations train with vs without tag and ensemble.

### 2. Dictionary / glossary substitution

**Setup**: bilingual lexicon (10K-100K word/phrase pairs).
**Apply**: take real source sentences; substitute words/phrases with target-language equivalents from lexicon.
**Result**: pairs of (mixed source, real target) — code-switched data.

Useful for:
- Building cross-lingual signal when no MT baseline exists.
- Class 0-1 with only a dictionary.
- Domain adaptation (medical/legal glossaries).

Limitations:
- No syntactic adjustment (just word swap).
- Output is code-switched, not natural.
- Quality bounded by dictionary quality.

### 3. Pivot MT

**Setup**: high-quality En→Intermediate (e.g., En→De) + decent Intermediate→Target (e.g., De→Yor).
**Apply**: translate corpus En → De → Yor.
**Result**: synthetic En-Yor pairs via pivot.

Often beats direct En-Yor when direct pair is much weaker than En-De.

Limitations:
- Cumulative error (En→De+0.05 BLEU loss × De→Yor+0.05 BLEU loss = 0.10 loss).
- Loses nuance specific to source-target pair.
- Loses gender/honorific markers absent in pivot but present in target.

## Quality control for synthetic data

After generation:
1. Round-trip check: forward-MT a sample back to source; compare with original. Round-trip BLEU ≥ 30 = reasonable.
2. Length-ratio filter (same as real bitext).
3. Native-speaker spot-check 100 samples.
4. Compute synthetic vs real ratio; recommend ≤ 5x synthetic / real for stable training.

## Mixing synthetic + real

| Ratio (synthetic / real) | Behavior |
|---|---|
| ≤ 1× | Synthetic boosts marginally |
| 1-5× | Synthetic clearly helps; standard practice |
| 5-20× | Diminishing returns; synthetic dominates |
| > 20× | Risk: model learns synthetic noise |

Common production: 3-5× synthetic for class 1-2 pairs.

## Anti-patterns

- **Back-translation with T=0**: translationese collapse.
- **Forward-translating the same model's output back as training data** (model collapse): only use back-translation, not forward-translation, for self-training.
- **Pivoting through a near-target language without quality check on intermediate pair**: errors compound silently.
- **Dictionary substitution without syntactic post-processing**: code-switched output is not natural target text.
- **Mixing synthetic + real without `<synthetic>` tag**: model can't learn to discount synthetic noise.

## See also

- **Sennrich, R., et al.** (2016). *Improving Neural Machine Translation Models with Monolingual Data* (back-translation). ACL.
- **Edunov, S., et al.** (2018). *Understanding Back-Translation at Scale*. EMNLP.
- **Burchell, L., et al.** (2024). *Scaling Low-Resource MT via Synthetic Data*. (Recent practitioner survey.)
- **Kim, Y., et al.** (2019). *Pivot-based Transfer Learning for Neural Machine Translation between Non-English Languages*. EMNLP.
