# Mining Recipes — Reference

Loaded by `magic-linguistic-bitext` Step 2.

## Embedding model selection

| Model | Languages | Strengths | Weaknesses | Best for |
|---|---|---|---|---|
| **LASER3** (Meta, 2022) | 200 | Wide coverage; mature | Bantu + Americas gaps; 1024-dim | European, Indic, SEA, CJK |
| **SONAR** (Meta, 2024) | 200+ | Better Bantu/Americas; sentence + speech | Larger model | African, Indigenous Americas, mixed-script |
| **LaBSE** (Google, 2020) | 109 | Strong cross-lingual; well-supported | Smaller language list | Common pairs; bilingual fine-tune |
| **Multilingual MiniLM** | varies | Lightweight | Lower recall | Compute-constrained |

Recommendation: **LASER3 for default + SONAR for African/Americas/mixed-script**.

## NLLB-style mining pipeline

The standard recipe (NLLB 2022, refined for OLDI 2024):

1. **Embed** every sentence in source corpus + every sentence in target corpus.
2. **Margin retrieval**: for each source sentence, find top-K target candidates by cosine; compute *margin* = top-1 / mean(top-K). Higher margin = more distinctive match.
3. **Threshold**: keep pairs with margin ≥ T (default 1.06; lower for LR).
4. **Symmetric matching**: keep pairs that are mutual top-1 within margin threshold.
5. **Post-filter**: language ID per side, length ratio, dedup.

## Vecalign-specific recipe

Vecalign is a sentence aligner (different from mining). Use when you have document-aligned pairs and need sentence-aligned output (Bible chapters, parliamentary proceedings, Wikipedia articles).

```
1. Pre-segment both sides into sentences (LASER's segmenter or sacremoses).
2. Embed each sentence (LASER3 or SONAR).
3. Run Vecalign with default DP-overlap settings.
4. Optional: filter by score threshold (Vecalign returns scores; lower = better).
5. Output: 1-1, 1-2, 2-1, 2-2, etc. alignments.
```

For Bibles specifically: Vecalign reaches 95%+ recall with default settings on most language pairs.

## hunalign (legacy)

Length-based aligner. Older but still useful when:
- No GPU available for embedding-based methods.
- Pre-segmented texts.
- Comparable lengths (no major insertion/deletion).

Otherwise, prefer Vecalign.

## Bleualign (MT-based)

Uses an existing MT system to align by translating one side and then aligning by BLEU. Useful when:
- You already have a reasonable MT baseline.
- Source/target are very different lengths.

Catch-22 for Class 0-1: you don't have an MT baseline yet, so Bleualign isn't usable.

## CCMatrix / CCAligned (large-scale Common Crawl mining)

Pre-mined parallel data from Common Crawl. Useful as starting point but:
- Quality varies; per-pair audit needed.
- Older snapshots may be in pretrain (contamination risk).
- Per-page rights uncertain.

For new projects, prefer mining your own + using CCMatrix as baseline reference.

## OPUS

The aggregator. https://opus.nlpl.eu/ has parallel data from many sources (TED, news, OpenSubtitles, etc.). Use as starting point + audit per source for license + quality.

For low-resource, OPUS coverage varies wildly: Yoruba has ~1.5M pairs; Inuktitut has ~5M (Hansard-dominated); Cherokee has ~50K.

## Recommended pipeline for new low-resource pair

```
1. Pull existing OPUS data for the pair.
2. Audit quality (sample 100 pairs; flag bad sources).
3. If insufficient (< 100K usable pairs), mine from monolingual:
   a. Embed source + target with LASER3 (or SONAR for African/Americas).
   b. Margin retrieval at threshold appropriate for pair class.
   c. Symmetric filter.
   d. Length-ratio + LID post-filter.
4. If still insufficient, generate synthetic via back-translation / pivoting.
5. Audit register balance.
6. Output bitext manifest.
```

## Refresh procedure

- LASER3 is stable as of 2022; check for SONAR-2 release annually.
- NLLB recipe stable; check WMT findings for new mining advances each year.
- OPUS adds new corpora monthly; re-check before any new low-resource project.

## See also

- **Costa-jussà et al.** (2022). NLLB-200 paper.
- **Thompson, B., & Koehn, P.** (2019). *Vecalign: Improved Sentence Alignment in Linear Time and Space*. EMNLP.
- **Schwenk, H., et al.** (2021). *CCMatrix: Mining Billions of High-Quality Parallel Sentences on the Web*. ACL.
- **Heffernan, K., et al.** (2022). *Bitext Mining Using Distilled Sentence Representations* (LASER3). EMNLP.
- SONAR repo: https://github.com/facebookresearch/SONAR
