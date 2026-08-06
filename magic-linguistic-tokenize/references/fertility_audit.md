# Fertility Audit — Reference

Loaded by `magic-linguistic-tokenize` Step 1.

## What fertility is

**Fertility = number of tokens / number of whitespace-separated words** in a held-out sample.

- English on tiktoken-cl100k_base (GPT-3.5/4): ~1.4 tokens/word.
- English on Llama-3 tokenizer: ~1.3 tokens/word.
- English on mBART tokenizer: ~1.2 tokens/word.

These baselines are the **denominator** for cross-language ratio comparisons.

## Cached baselines (snapshot 2026-04-23)

`scripts/fertility_audit.py` ships these baselines per (tokenizer, language) pair, computed on a fixed Wikipedia sample of 1000 sentences:

| Tokenizer | English | Yoruba | Khmer | Vietnamese | Mandarin | Turkish | Inuktitut |
|---|---|---|---|---|---|---|---|
| tiktoken-cl100k_base | 1.4 | 3.4 | 4.2 | 2.1 | 1.6 | 2.8 | 6.1 |
| Llama-3 (128K) | 1.3 | 2.9 | 3.7 | 1.9 | 1.4 | 2.4 | 5.4 |
| mBART (250K) | 1.2 | 2.0 | 2.4 | 1.5 | 1.3 | 1.7 | 3.8 |
| NLLB (256K) | 1.3 | 1.8 | 2.0 | 1.5 | 1.3 | 1.6 | 3.2 |
| BLOOM (250K) | 1.4 | 2.1 | 2.3 | 1.6 | 1.4 | 1.8 | 3.6 |
| AfroLM-6.5K | 6.5 | 1.6 | n/a | n/a | n/a | n/a | n/a |

(Take-away: language-specialized tokenizers like AfroLM achieve near-baseline fertility on the target at the cost of being terrible on English. The right choice depends on whether you need both.)

## Interpretation table

| Fertility ratio (target/English) | Interpretation | Action |
|---|---|---|
| ≤ 1.5 | Tokenizer covers target well | No action |
| 1.5 - 2.0 | Mild penalty | Optional vocab extension; depends on cost sensitivity |
| 2.0 - 3.0 | Significant penalty | Vocab extension recommended |
| ≥ 3.0 | Severe penalty | Vocab extension MANDATORY |
| ≥ 5.0 | Tokenizer is essentially failing for this language | Train new tokenizer or use language-specialized base |

## What "high fertility" actually costs

For a fixed 4096-token context window with English baseline 1.4:

| Target fertility | Effective context (target words) | Inference cost ratio | Training cost ratio |
|---|---|---|---|
| 1.4 | 2926 | 1.0× | 1.0× |
| 2.0 | 2048 | 1.4× | 1.4× |
| 3.0 | 1365 | 2.1× | 2.1× |
| 5.0 | 819 | 3.6× | 3.6× |
| 7.0 | 585 | 5.0× | 5.0× |

The ratio appears ~equal to fertility/baseline because token-level operations dominate for both. So fertility 3.0 ≈ 2× the inference cost vs English. This is real money in production.

## How to compute fertility correctly

```python
def fertility(text: str, tokenizer) -> float:
    words = text.split()  # whitespace-separated tokens; not the right "word" definition for all languages
    n_words = len(words)
    n_tokens = len(tokenizer.encode(text))
    return n_tokens / n_words
```

**Caveats and corrections:**
- For languages without spaces (Mandarin, Japanese, Thai): split by character or use a language-specific word segmenter (Jieba for Mandarin, MeCab for Japanese, PyThaiNLP for Thai). Otherwise "words" undercounts by ~10×.
- For agglutinative languages where a "word" carries multiple morphemes: fertility may UNDER-state the cost. Some research uses morphemes as denominator (lower fertility ratio but more meaningful).
- For tone languages, tone marks should NOT be stripped before tokenization (else fertility looks artificially low).

## Sample size

- 1000 sentences (Wikipedia held-out) is the standard for reproducible cross-tokenizer comparisons.
- 100 sentences is acceptable for quick triage.
- < 50 sentences is too few — variance dominates.
- For domain-specific (medical, legal, code), use a domain-specific sample; cross-domain fertility differences are 30%+.

## Common confusions

1. **"Vocab size" vs "fertility"**: a 250K-vocab tokenizer can still have fertility 5 on a low-resource language if the vocab is dominated by English. Vocab size is not coverage.
2. **"Coverage" vs "fertility"**: SentencePiece's `character_coverage` is a *training-data* parameter, not a runtime metric. Fertility measures the result.
3. **"OOV rate" vs "fertility"**: with byte fallback, OOV rate is 0% but fertility can be huge (every UTF-8 byte = 1 token).
4. **Per-language vs aggregate**: a multilingual tokenizer has different fertility per language. "Mean fertility" is not what you want — surface per-language table.

## See also

- Rust et al. (2021), *How Good is Your Tokenizer? On the Monolingual Performance of Multilingual Language Models* (ACL).
- Ahia et al. (2023), *Do All Languages Cost the Same? Tokenization in the Era of Commercial Language Models* (EMNLP).
- Land et al. (2024), *Fishing for Magikarp: Automatically Detecting Under-trained Tokens in Large Language Models* (EMNLP).
- Petrov et al. (2023), *Language Model Tokenizers Introduce Unfairness Between Languages*.
