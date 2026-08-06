# Byte Fallback Policy — Reference

Loaded by `magic-linguistic-tokenize` Step 4 before disabling byte fallback.

## What byte fallback does

When the tokenizer encounters a character not in its vocabulary, instead of producing `<unk>`, it falls back to encoding the character as its UTF-8 bytes (each byte → one token, typically `<0x00>` through `<0xFF>` reserved tokens).

Cost: 1-4 tokens per OOV character (UTF-8 multi-byte sequences).
Benefit: zero `<unk>` rate; deterministic encode/decode; round-trip preservation.

## When byte fallback is MANDATORY

| Condition | Why |
|---|---|
| Class 0-2 language | OOV is GUARANTEED — fall back, don't lose information |
| Han (CJK) script | 5000+ rare characters won't fit in 100K vocab; rare names matter |
| Arabic (with diacritics) | Harakat-marked text is OOD vs un-vocalized training |
| Code-heavy content | Special chars, foreign function names, Unicode symbols |
| Multi-script corpus | Predicting all script-character combinations exhaustively is impossible |
| Emoji / symbols | Endlessly extensible |
| Any production system handling user input | You can't predict what users will type |

## When byte fallback is OPTIONAL (still usually correct)

| Condition | Justification for OFF |
|---|---|
| Class 5 + Latin only + curated training corpus + closed input domain | Vocab covers everything; byte fallback dilutes attention |
| Tokenizer benchmark experiments where you need clean OOV-rate measurement | Measurement requires controlled OOV |
| Tiny on-device inference where every token-id slot matters | 256 reserved byte-tokens are real cost |

For most production LLM work: **leave byte fallback ON**.

## How byte fallback interacts with fertility

For OOV-heavy text, byte fallback can SPIKE fertility (because each unknown character becomes 1-4 tokens of byte-fallback). Two-step diagnosis:

1. Measure fertility WITH byte fallback → high.
2. Measure OOV rate (count of byte-fallback tokens / total tokens).

If OOV rate > 5%: vocab is failing → vocab extension or new tokenizer needed.
If OOV rate < 1% AND fertility is still > 2× English: tokenizer is over-segmenting (vocab covers chars but creates long subword sequences) → adjust unigram coverage / vocab size.

## SentencePiece byte-fallback config

```python
import sentencepiece as spm
spm.SentencePieceTrainer.train(
    input="training.txt",
    model_prefix="tokenizer",
    vocab_size=64000,
    model_type="unigram",
    byte_fallback=True,  # critical
    character_coverage=0.99999,
    # The 256 byte tokens are reserved automatically.
    # If you also want unk_surface for the rare cases byte_fallback can't handle:
    unk_surface=" ⁇ ",
)
```

After training, verify byte tokens exist:

```python
sp = spm.SentencePieceProcessor()
sp.load("tokenizer.model")
# Check that <0x00> through <0xFF> are in vocab
byte_tokens = [sp.id_to_piece(i) for i in range(sp.vocab_size()) if sp.id_to_piece(i).startswith("<0x")]
assert len(byte_tokens) == 256, f"byte fallback not configured: only {len(byte_tokens)} byte tokens"
```

## HuggingFace tokenizers byte-fallback

Different mechanisms:
- **GPT-2 / GPT-4 (byte-level BPE)**: every byte is in vocab; no separate fallback. Inherently byte-safe.
- **Llama / Llama-2 / Llama-3 (SentencePiece-derived BPE)**: byte fallback configurable.
- **mBART / NLLB / BLOOM (SentencePiece Unigram)**: byte fallback present.

For Llama-style tokenizers loaded via HF, check the tokenizer config:

```python
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
# Look for byte fallback in special tokens
print([t for t in tok.get_vocab() if t.startswith("<0x")][:10])
```

## Common pitfalls

- **Disabling byte fallback "to save vocab slots"**: 256 tokens is a tiny slice of any modern vocab (32K+). Disabling for this reason is a false economy.
- **Assuming byte fallback handles everything well**: it does handle correctness, but each multi-byte char costs 2-4 tokens. Vocab extension for high-frequency rare chars is still warranted.
- **Forgetting to reserve byte token IDs in fine-tuning**: if byte tokens get clobbered by fine-tuned added tokens, the bytefallback cascade breaks.
- **Mixing byte-fallback-on training corpus with byte-fallback-off inference**: tokenizer mismatch → encoding-decoding asymmetry → silent corruption.

## See also

- **Sennrich et al. (2016)**, *Neural Machine Translation of Rare Words with Subword Units* (ACL) — original BPE.
- **Kudo (2018)**, *Subword Regularization* (ACL) — Unigram and Unicode handling.
- SentencePiece byte_fallback docs: https://github.com/google/sentencepiece/blob/master/doc/options.md
- Llama-3 tokenizer report: https://github.com/meta-llama/llama3
