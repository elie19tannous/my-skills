# Active Learning for Annotation — Reference

Loaded by `magic-linguistic-annotate` Step 5.

## When to use active learning

When the annotation budget is limited (which is always for low-resource):
- 100 - 10,000 items target.
- A model is available (zero-shot, few-shot, or trained on small seed).
- Active selection > random sampling for catching informative items.

## Three main strategies

### 1. Random sampling (baseline)

Pure uniform random. Always works as baseline. Under-samples rare classes; doesn't exploit any model signal.

### 2. Uncertainty sampling

Use a model to score each unlabeled item by uncertainty (entropy of predicted distribution). Annotate the most uncertain.

Variants:
- **Least confidence**: 1 - max(p).
- **Margin**: p_top - p_second.
- **Entropy**: H(p).

Pros: targets model blind spots.
Cons: bias toward model failure modes — if model is bad in one direction, you get biased sample.

### 3. Diversity / clustering-based

Cluster the unlabeled pool (using sentence embeddings); sample diverse items per cluster.

Pros: best coverage of distribution; less sensitive to model quality.
Cons: doesn't exploit model uncertainty.

### 4. Hybrid (recommended for production)

Combine uncertainty + diversity:
1. Score items by uncertainty.
2. Cluster top-K most uncertain.
3. Sample one item per cluster.

Best in practice. Most active-learning papers since 2020 use variants of this.

## Per-resource recommendations

| Setting | Recommended |
|---|---|
| Class 0-1 + no model | Diversity-only (no model to drive uncertainty) |
| Class 0-1 + zero-shot model | Hybrid (diversity dominant) |
| Class 2-3 + small model | Uncertainty (model is reasonable; trust it) |
| Class 4-5 | Random + occasional uncertainty (model is good; bigger gains from random coverage) |

## Pool re-pooling

After each batch, re-evaluate the pool with the updated model:
- "Uncertain" items often become "easy" once labeled neighbors exist.
- New items may surface as uncertain that weren't before.
- Re-pool every batch (or every 2-3 batches if compute-limited).

## Stopping criterion

Stop when:
- Held-out eval plateaus (no significant gain over last N batches).
- Budget exhausted.
- Model confidence is uniformly high on remaining pool.

## Common AL mistakes

- **Selecting all top-K-uncertain items at once**: they're often near-duplicates; diversity step required.
- **Not re-pooling after each batch**: AL signal stales.
- **Using AL on a tiny seed**: model is too weak to give meaningful uncertainty; start with random.
- **Skipping pool curation**: if pool has noise (wrong-language, off-domain), AL surfaces noise as "uncertain".
- **Reporting AL gains without random baseline**: AL often gets 10-20% gain over random; without baseline, can't tell.

## Tooling

| Tool | Strengths |
|---|---|
| modAL | Python AL library; multiple strategies |
| Prodigy | Built-in active-loop UI |
| Label Studio | ML backend integration for AL |

## See also

- **Settles, B.** (2009). *Active Learning Literature Survey*. UW Tech report.
- **Lowell, D., Lipton, Z. C., Wallace, B. C.** (2019). *Practical Obstacles to Deploying Active Learning*. EMNLP.
- **Sener, O., & Savarese, S.** (2018). *Active Learning for Convolutional Neural Networks: A Core-Set Approach*. ICLR.
- **Margatina, K., et al.** (2021). *Active Learning by Acquiring Contrastive Examples*. EMNLP.
