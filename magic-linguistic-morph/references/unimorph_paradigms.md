# UniMorph Paradigms — Reference

Loaded by `magic-linguistic-morph` Step 1.

## What UniMorph is

UniMorph is a cross-lingual gold-standard morphological-paradigm catalog. Each entry: lemma + feature bundle → surface form. Covers 100+ languages with varying depth. https://unimorph.github.io/

Format example:
```
beat   beating   V;V.PTCP;PRS
beat   beats     V;3;SG;PRS
beat   beat      V;PST
beat   beat      V;V.PTCP;PST
```

## Coverage tiers (snapshot 2026-04-23)

| Coverage | Languages (selected) | Lemmas per |
|---|---|---|
| Deep (>10K lemmas) | Turkish, Finnish, Russian, Czech, Polish, Spanish, Portuguese, Latin | 10K-100K |
| Mid (1K-10K) | Yoruba, Hindi, Tamil, Hebrew, Arabic, Hungarian, Estonian, Georgian | 1K-10K |
| Shallow (<1K) | Many Niger-Congo, some Indigenous Americas, smaller Indic | 100-1K |
| Absent | Most class 0-1; many endangered | 0 |

## What UniMorph is good for

- **Paradigm-completion augmentation**: 10× expand small corpora.
- **Morphological tagger training data**: gold inflections.
- **Inflection-prediction baselines** (SIGMORPHON shared tasks).
- **Tokenizer audit**: morpheme alignment with paradigm forms.

## What UniMorph is NOT for

- Treebanks (use UD).
- Word-sense / lexical semantics (use WordNet/OMW).
- Sentence-level parsing (use UD or stanza).

## Per-language quick lookup

| Language | UniMorph status | Notes |
|---|---|---|
| Turkish (tur) | DEEP | Standard agglutinative test case |
| Finnish (fin) | DEEP | 15+ noun cases |
| Russian (rus) | DEEP | Fusional Slavic |
| Yoruba (yor) | MID | Tone marking included; sparse for some POS |
| Hindi (hin) | MID | Devanagari + Latin transliteration variants |
| Tamil (tam) | MID | Dravidian agglutinative |
| Arabic (arb) | MID | Templatic — paradigms encode root + pattern |
| Hebrew (heb) | MID | Templatic — like Arabic |
| Khmer (khm) | SHALLOW | Limited; consider FieldDB resources |
| Twi (twi) | SHALLOW | Tone-aware paradigms patchy |
| Inuktitut (iku) | SHALLOW | Polysynthetic; FST (HFST) better than UniMorph alone |
| Navajo (nav) | ABSENT | No usable UniMorph; community-collected only |
| Cherokee (chr) | ABSENT | None; FST partial |

## Refresh

UniMorph receives quarterly updates. Re-check before any major project. Some updates add paradigms; others fix annotation errors.

## See also

- **Kirov, C., et al.** (2018). *UniMorph 2.0: Universal Morphology*. LREC.
- **Batsuren, K., et al.** (2022). *UniMorph 4.0: Universal Morphology*. LREC. — Current version.
- SIGMORPHON shared task repos: https://github.com/sigmorphon
