# Confusables (TR39) — Reference

Loaded by `magic-linguistic-scripts` before deduplication, bitext mining, or any pipeline step that compares strings.

## What confusables are

Different Unicode code points that render visually identical (or nearly so):

| Latin | Cyrillic look-alike | Greek look-alike | Other |
|---|---|---|---|
| a (U+0061) | а (U+0430) | α (U+03B1) | |
| e (U+0065) | е (U+0435) | | |
| o (U+006F) | о (U+043E) | ο (U+03BF) | |
| p (U+0070) | р (U+0440) | ρ (U+03C1) | |
| c (U+0063) | с (U+0441) | | |
| y (U+0079) | у (U+0443) | | |
| H (U+0048) | Н (U+041D) | Η (U+0397) | |
| K (U+004B) | К (U+041A) | Κ (U+039A) | |
| 0 (U+0030) | | | О-mongolian, ০ (Bengali zero), ٠ (Arabic zero) |
| I (U+0049) | | | l (Latin l), 1 (digit 1), Ι (Greek capital iota) |

Plus thousands more in TR39's full skeleton table.

## Why this matters for ML pipelines

### Web crawl ingestion
~5-15% of multi-script web crawl is confusable-duplicated when pages mix scripts (Cyrillic Wikipedia editor inserting Latin characters; or vice-versa). Without confusable folding before dedup, you train on near-duplicate noise.

### Bitext mining
Sentence-pair miners use cosine similarity of embeddings + character-overlap as filters. Confusables inflate character-overlap (visual identity → numeric equality after fold), pushing noise pairs above the margin threshold. Apply fold *before* margin filtering.

### Fertility inflation
Tokenizers see "café" (Latin) and "cafe with Greek a" as different tokens. Vocab gets bloated with look-alike entries → genuine OOV grows.

### Security vector (less common in our context)
Homograph attacks on URLs (раypal.com vs paypal.com). Not our problem in linguistic ML, but mention because TR39 was originally a security spec.

## How to apply

```python
import unicodedata

# Approximation of TR39 skeleton (real TR39 is much larger).
# For production, use `confusable-homoglyphs` or `unicode_skeleton` libraries.
SIMPLE_FOLD = {
    'а': 'a', 'е': 'e', 'о': 'o', 'р': 'p', 'с': 'c', 'у': 'y',
    'А': 'A', 'Е': 'E', 'О': 'O', 'Р': 'P', 'С': 'C', 'Х': 'X', 'Н': 'H', 'К': 'K',
    # ... many more
}

def fold_for_dedup_key(s: str) -> str:
    s = unicodedata.normalize('NFC', s)
    return ''.join(SIMPLE_FOLD.get(c, c) for c in s)
```

For full TR39, install `confusable-homoglyphs` (Python) or use ICU's `Transliterator("Any-NFKD; Any-Lower")` as an approximation.

## Application policy

| Use case | Mode |
|---|---|
| Dedup key (compute hash) | **fold** — store fold in keying-only; original text untouched |
| Bitext alignment scoring | **fold** for character-overlap term; original kept for actual training pair |
| Storage of training data | **NEVER fold** — keep original |
| Search index | **fold** — index supports both folded and original lookup |

**The rule:** fold for *comparison*, never for *storage*.

## Detection vs folding

Two distinct operations:

- **Detect**: scan corpus for confusable hits, report positions + counts. Output: a report. Original text preserved.
- **Fold**: apply the skeleton mapping. Output: transformed strings. Use only for dedup keys.

`scripts/detect_confusables.py` supports both modes.

## Detection report structure

```json
{
  "file": "input.txt",
  "total_chars": 15234,
  "confusable_hits": 42,
  "by_pair": {
    "Latin-Cyrillic": 28,
    "Latin-Greek": 11,
    "Latin-Arabic": 3
  },
  "samples": [
    {"position": 1234, "context": "...раypal...", "expected_script": "Latin", "found": "Cyrillic 'р'"},
    ...
  ]
}
```

## Edge cases

- **Intentional mixing** (e.g., a Greek letter in a math equation in English text): not a confusable, a legitimate use. Don't fold blindly. Detection-mode reports let humans audit.
- **"Cyrillic in Russian text" is not a confusable.** Confusables are only when the *script context* doesn't match.
- **TR39 skeleton evolves** with each Unicode release. Pin a version (we use Unicode 15.1 / 2026-04-23 cached snapshot).
- **Homograph URLs** are usually filtered at the browser/registrar level. Don't try to be a security tool.

## When NOT to fold

- Datasets that explicitly test character-level robustness (adversarial NLP).
- Forensic / authorship analysis.
- Endangered-language corpora where script-mixing is documented community usage (some Indigenous community typing practices use Latin look-alikes when keyboards are limited).

## See also

- Unicode Technical Standard #39: https://unicode.org/reports/tr39/
- `confusable_homoglyphs` (Python lib): https://github.com/vhf/confusable_homoglyphs
- ICU `Skeleton` algorithm: https://unicode-org.github.io/icu/userguide/transforms/general/
