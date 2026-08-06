# Deduplication — Reference

Loaded by `magic-linguistic-corpus` Step 5.

## Three layers of dedup

1. **Exact**: identical strings after normalization. Cheap; always run first.
2. **Near-duplicate (MinHash)**: Jaccard-similarity over character n-grams. Catches paraphrases, formatting variants.
3. **Semantic (embedding)**: cosine over sentence embeddings. Catches re-translations and paraphrases that share meaning but few characters. Slow; use selectively.

## MinHash configuration for low-resource

| Param | Default (general) | Low-resource recommendation | Why different |
|---|---|---|---|
| `num_perm` | 128 | **256** | Better Jaccard estimation for short docs |
| `threshold` | 0.8 | **0.9** for class 0-2, **0.85** otherwise | 0.8 over-merges short content |
| Shingle size (chars) | 5 | 5 for Latin/Cyrillic; **3 for Han / Indic** | Shorter shingles catch CJK-style segmentation |
| Shingle type | character | character (NOT word) | Word shingles fail on space-less scripts |

The 0.8 threshold comes from large-corpus dedup where most "near-duplicates" are real duplicates. For low-resource corpora with smaller documents, 0.9 keeps more legitimately-distinct entries.

**Concrete impact:** on MasakhaNER Yoruba, threshold 0.8 removes 28% of entries (over-aggressive); threshold 0.9 removes 6% (correct).

## Pre-dedup steps (mandatory)

Before MinHash:
1. Unicode normalize via `magic-linguistic-scripts` (NFC).
2. Confusable fold via `magic-linguistic-scripts` (TR39 — fold ONLY for the dedup key, not stored text).
3. Lower-case + strip whitespace runs (for the key only).
4. Remove BOM, ZWJ/ZWNJ from key (keep in stored text per script policy).

Without these, look-alike + case-variant duplicates survive.

## Dedup-stat reporting

For each dataset / merged mix, report:

```json
{
  "input_docs": 100000,
  "after_exact_dedup": 95000,
  "after_minhash_dedup": 87500,
  "exact_duplicate_ratio": 0.05,
  "near_duplicate_ratio": 0.075,
  "config": {"num_perm": 256, "threshold": 0.9, "shingle_size": 5},
  "snapshot_date": "2026-04-23"
}
```

## Cross-dataset dedup

When merging N datasets, run dedup AFTER concatenation, not within each. CulturaX + MADLAD-400 + Wikipedia all have substantial overlap (mC4-derived); per-dataset dedup misses cross-source duplicates.

## Dedup vs decontamination

These are different:
- **Dedup** removes duplicates from training mix (data quality).
- **Decontamination** removes test-set leakage from training (eval validity).

Dedup uses MinHash on full text. Decontamination uses 13-gram exact match (the GPT-3 / OpenAI standard).

See `contamination_audit.md`.

## Common dedup mistakes

- **Threshold too low (0.8)** for short or low-resource content → over-merges.
- **Word shingles for Han / Khmer / Thai** → useless (no spaces).
- **Skipping confusable fold** → Latin/Cyrillic look-alikes survive.
- **Per-dataset dedup only** → cross-source duplicates survive in merged corpus.
- **MinHash without `num_perm` ≥ 128** → Jaccard estimation noisy for short docs.

## See also

- **Lee, K., et al.** (2022). *Deduplicating Training Data Makes Language Models Better*. ACL.
- **Carlini, N., et al.** (2023). *Quantifying Memorization Across Neural Language Models*. ICLR.
- `datasketch` Python library for MinHash: https://github.com/ekzhu/datasketch
- Apache Spark MinHashLSH for cross-dataset dedup at scale.
