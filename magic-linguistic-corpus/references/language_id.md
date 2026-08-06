# Language Identification — Reference

Loaded by `magic-linguistic-corpus` Step 3.

## The three main LID models

| Model | Languages | Granularity | Best for | Source |
|---|---|---|---|---|
| **GlotLID** (2024) | 2000+ | paragraph / sentence | low-resource; recommended default | Kargaran et al. 2023, EMNLP |
| **FastText langid 176** | 176 | paragraph / sentence | high-resource; fast | Joulin et al. 2017 |
| **CLD3** (Google) | 107 | sentence | legacy; small models | https://github.com/google/cld3 |
| **NLLB-LID** | 218 | sentence | NLLB-aligned; high recall on Bantu/Americas | Costa-jussà et al. 2022 |

**Default recommendation:** GlotLID for low-resource (Class 0-3). FastText for Class 4-5 if speed matters. NLLB-LID specifically for African / Indigenous Americas where GlotLID may have gaps.

## Document vs paragraph vs sentence granularity

| Granularity | Pro | Con | Use when |
|---|---|---|---|
| Document | Fast | Misses code-switching, multilingual quotes, multi-script docs | Class 5 monolingual web crawl |
| **Paragraph** | Catches most code-switching; reasonable speed | Some short paragraphs unreliable | **Default for LR work** |
| Sentence | Maximally precise | Slow; very short sentences unreliable | Bitext mining where per-sentence LID is critical |

## Why paragraph-level is the floor for LR work

1. Hinglish / Chinglish / Spanglish documents often have alternating-paragraph languages.
2. Wikipedia code-switches to source language for quotes (Yoruba article quoting English source).
3. Bible-NLP datasets sometimes mix verses from related languages.
4. Multi-script PDF OCR results often have text in multiple languages.
5. Low-resource Wikipedia editors sometimes paste English boilerplate.

Document-level LID labels the whole thing as one language → 5-30% of paragraphs are wrong-language. Paragraph-level LID finds and removes them.

## LID confidence thresholds

| Threshold | Behavior |
|---|---|
| ≥ 0.95 | Accept |
| 0.80 - 0.95 | Accept with flag (audit if downstream issues) |
| 0.50 - 0.80 | Reject (likely mixed or unreliable) |
| < 0.50 | Reject |

For class 0-1 where any data is valuable, lower thresholds (≥ 0.75 accept) — but flag and spot-check.

## Common LID failures

| Failure mode | Symptom | Fix |
|---|---|---|
| Hindi mis-tagged as 'hi' from Hinglish/Latin transliteration | LID confident but content is in Latin script | Combine LID + script detection |
| Macrolanguage confusion | Cantonese tagged as 'zh' (zho macro) | Use disambiguating LID (NLLB-LID better than FastText for zho) |
| Code-switched text labeled as dominant language | Sub-paragraph minority language slips through | Sentence-level for sensitive applications |
| Very short text (< 5 words) unreliable | LID flips between predictions | Min-length filter (≥ 5-10 words) |
| Bible-NLP language tags inaccurate for some translations | Tag says language X, content language Y | Spot-check sample per Bible source |

## Per-paragraph LID workflow

```python
# Pseudocode (Phase 2+ wires real models)
import glotlid

def lid_paragraphs(doc: str, target_lang: str, min_conf: float = 0.85, min_words: int = 5):
    paragraphs = split_paragraphs(doc)
    keep, discard = [], []
    for p in paragraphs:
        if len(p.split()) < min_words:
            discard.append(("too_short", p))
            continue
        pred, conf = glotlid.predict(p)
        if pred == target_lang and conf >= min_conf:
            keep.append(p)
        else:
            discard.append((f"lid_{pred}_{conf:.2f}", p))
    return keep, discard
```

## See also

- **Kargaran, A., Imani, A., Yvon, F., Schütze, H.** (2023). *GlotLID: Language Identification for Low-Resource Languages*. EMNLP.
- **Joulin, A., et al.** (2017). *Bag of Tricks for Efficient Text Classification* (FastText). EACL.
- **Costa-jussà et al.** (2022). NLLB-200, includes NLLB-LID.
