# Unicode Normalization — Reference

Loaded by `magic-linguistic-scripts` Step 3 before any NFKC application or per-script policy decision.

## The four normalization forms (UAX #15)

| Form | What it does | Reversible? | Use for |
|---|---|---|---|
| **NFD** | Canonical decomposition (precomposed → base + combining marks) | YES (round-trip via NFC) | Manipulating diacritics individually |
| **NFC** | Canonical composition (combining marks → precomposed where possible) | YES (round-trip via NFD) | DEFAULT for storage and processing |
| **NFKD** | Compatibility decomposition (incl. compat chars) | NO (information loss) | Search-time only |
| **NFKC** | Compatibility composition | NO (information loss) | Search/dedup-time only, with explicit consent |

## What NFKC destroys (and why this matters)

NFKC collapses these — irrecoverably:

| Source | After NFKC | Loss |
|---|---|---|
| ﬁ (U+FB01 ligature) | fi | Visual distinction (matters for OCR re-rendering) |
| ﬃ (U+FB03) | ffi | Same |
| ſ (U+017F long-s) | s | Historical-text distinction destroyed |
| ㍿ (U+337F square era marker) | 株式会社 | Compact form lost |
| ³ (U+00B3 superscript 3) | 3 | Mathematical notation flattened |
| ! (U+FF01 fullwidth) | ! (U+0021 ASCII) | Asian typography loses fullwidth signal |
| ﷽ (U+FDFD) | بسم الله الرحمن الرحيم | Arabic ligature → expansion (changes length, alignment) |
| ① (U+2460 circled 1) | 1 | List-marker information destroyed |

**For modern typed text in major scripts**, NFKC is *often* harmless. For:
- Historical text → BLOCK NFKC (long-s).
- Arabic → BLOCK NFKC (presentation forms FE70-FEFF carry contextual rendering).
- Mathematical notation → BLOCK NFKC.
- Asian typography (full-width chars are stylistic) → BLOCK NFKC unless you're flattening for search.

## When NFKC IS appropriate

- Building a **dedup key**: the folded form is what you compare; canonical storage stays NFC.
- Building a **search index**: same — store NFC, index NFKC.
- **Filename normalization** for cross-platform compatibility.
- **One-off cleanup** of OCR output where compatibility chars are clearly noise.

## NFC mistakes that bite later

- **Hash drift**: storing NFC but reading something that wasn't NFC-normalized → hashes mismatch → "file unchanged" assertions fail mysteriously.
- **NFD on macOS HFS+ filesystems**: macOS stores filenames in NFD. Reading filenames cross-platform breaks if you assume NFC. Always normalize on read.
- **Mixed forms in the same column**: especially common in CSV exports from spreadsheets — some cells precomposed, some decomposed. Normalize on ingest.
- **Order-dependent combining marks**: NFC normalizes the order of combining marks. Without normalization, "ä̀" with ¨ before ̀ vs ̀ before ¨ are different code-point sequences but visually identical. Dedup misses them without normalization.

## Implementation notes

Python:
```python
import unicodedata
text_nfc = unicodedata.normalize('NFC', raw)  # default for everything
text_nfkc = unicodedata.normalize('NFKC', raw)  # ONLY for dedup/search keys
```

For batch operations on millions of strings, prefer the C-implementation in `unicodedata` (already C). For SIMD-batched normalization on huge corpora, see `icu4py` or the Rust `unicode-normalization` crate via FFI.

## Per-script normalization quick-ref

| Script | NFC behavior notes |
|---|---|
| Devanagari | NFC composes vowel signs onto consonants. ZWJ/ZWNJ are preserved (semantic). |
| Tibetan | NFC handles stacked consonants; preserve ZWJ/ZWNJ. |
| Arabic | NFC handles base + diacritics. NFKC would collapse presentation forms — DO NOT. |
| Hebrew | NFC handles letter + niqqud. NFKC would collapse final-form letters in some pipelines — DO NOT. |
| Tamil | NFC composes vowel diacritics. Conjuncts via virama + consonant — NFC leaves intact. |
| Khmer | NFC handles complex sub-script diacritics. |
| Mongolian | Variation selectors carry significant meaning; NFC preserves them. |
| Modern Latin | NFC composes "é", "ü", etc. NFKC sometimes harmless but check ligatures first. |

## See also

- Unicode Standard Annex #15 (Normalization Forms): https://unicode.org/reports/tr15/
- Unicode Technical Standard #39 (Confusables): https://unicode.org/reports/tr39/
- ICU normalization: https://unicode-org.github.io/icu/userguide/transforms/normalization/
