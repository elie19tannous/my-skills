# SIGMORPHON Segmenters — Reference

Loaded by `magic-linguistic-morph` Step 3.

## What SIGMORPHON is

The Special Interest Group on Computational Morphology, hosting an annual shared task. Recent shared tasks (2022, 2023, 2024) have established SOTA on:
- Inflection generation (lemma + features → surface form).
- Morpheme segmentation (word → morpheme boundaries).
- Reinflection.
- Cross-lingual transfer.

## Segmenter selection (snapshot 2026-04-23)

| Method | When to use | Strength | Weakness |
|---|---|---|---|
| **SIGMORPHON 2022 segmenters** | General agglutinative | SOTA on shared task | Per-language model files |
| **Morfessor** (Smit et al.) | Old reliable; many languages | Mature; widely used | Outperformed by 2022+ neural |
| **MorPiece** | Hybrid BPE + morpheme | Good for tokenizer integration | Limited language coverage |
| **HFST/foma rule-based** | When good rules exist (FSTs) | Perfect for documented languages | Requires linguistic expertise |
| **stanza morphology** | Multi-language convenience | Easy API; UD-aligned | Quality varies per language |

## Per-tier recommendations

### Agglutinative (Turkic, Uralic, Bantu, Korean)

Recommended pipeline:
1. Try UniMorph if coverage exists → use directly.
2. SIGMORPHON 2023 winner if available for the language family.
3. Morfessor as fallback baseline.
4. Tokenizer with morpheme-aware initialization.

### Polysynthetic (Inuktitut, Navajo, Cherokee)

1. UniMorph if any coverage (rare).
2. HFST/foma analyzer if community has built one (check Apertium).
3. SIGMORPHON 2023 segmenter as fallback.
4. Per-morpheme tokenization mandatory.

### Templatic (Arabic, Hebrew, Amharic)

Different problem. Concatenative segmenters fail. Recommend:
1. **Farasa** for Arabic (root + pattern aware).
2. **YAP** for Hebrew.
3. **HornMorpho** for Amharic.
4. Build root-extractor + pattern-applier as preprocessing.

### Fusional with rich case (Slavic, Greek, Sanskrit)

- Morfessor handles fusional reasonably.
- stanza's morphology is good for major languages.

## Known coverage gaps

- Most class 0-1 languages lack any pre-trained segmenter.
- Many Indigenous Americas families have NO SIGMORPHON entries.
- Sign languages: out of scope.
- Newly-romanized languages: tokenizer-only is sometimes the best you can do.

## Integration into ML pipeline

Two integration patterns:

1. **Pre-tokenize** with morpheme segmenter before BPE. Improves fertility 30-50% for agglutinative class 1-2.
2. **Augment vocabulary** with morpheme inventory. Less invasive but requires vocab-extension work.

Hand-off: route to `magic-linguistic-tokenize` for vocab-extension audit after morphology integration.

## See also

- SIGMORPHON shared task repos: https://github.com/sigmorphon
- **Smit, P., et al.** (2014). *Morfessor 2.0: Toolkit for statistical morphological segmentation*. EACL.
- **Pasha, A., et al.** (2014). *MADAMIRA / Farasa* (Arabic).
- **Eshkol-Taravella, I., et al.** YAP Hebrew.
- **Gasser, M.** (2011). *HornMorpho* (Ge'ez family).
