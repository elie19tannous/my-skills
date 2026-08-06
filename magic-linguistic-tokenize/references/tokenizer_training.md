# Tokenizer Training (SentencePiece) — Reference

Loaded by `magic-linguistic-tokenize` Step 3 when training a new tokenizer or extending an existing one.

## Library choice

| Library | Strengths | Weaknesses | Use for |
|---|---|---|---|
| **SentencePiece** | Mature; Unigram + BPE; byte fallback; user-defined symbols | C++ binary; slower than HF tokenizers for inference | Training; production where you need byte fallback |
| **HuggingFace tokenizers (Rust)** | Fast inference; clean Python API | BPE only; less flexible Unigram | Inference; quick experimentation |
| **OpenAI tiktoken** | Fast; matches OpenAI exactly | English-biased; closed training | Only when matching OpenAI output |
| **Google sentencepiece-cli** | Ground truth | CLI only | Reference when debugging Python wrapper |

For LLM training: **SentencePiece for the train step** (best control), **HuggingFace tokenizers for inference** (faster, easier integration).

## BPE vs Unigram

| Aspect | BPE | Unigram |
|---|---|---|
| Algorithm | Greedy merge frequent pairs | Probabilistic LM over subword sequences |
| Determinism | Deterministic | Stochastic at training (deterministic at inference unless dropout used) |
| Empirical performance | Usually slightly worse than Unigram for low-resource | Usually slightly better; shines on morphologically rich languages |
| Compression | Often better | Often slightly worse |
| Subword regularization | BPE-dropout | Built-in (sample subword sequences during training) |
| Default for new tokenizers | Acceptable | **Recommended** by current research |

**Recommendation**: use `model_type=unigram` for new tokenizers unless you have a specific reason to match an existing BPE setup.

## Vocab size

| Vocab size | Use case |
|---|---|
| 8K-16K | Tiny / specialized; benchmarks only |
| 32K | Llama / Mistral baseline; English-dominant |
| 50K | GPT-2-style; English |
| 64K | Multilingual but conservative |
| 128K | Llama-3, ~5 high-resource languages |
| 200K-256K | mBART, NLLB, BLOOM — broad multilingual |
| 512K+ | XGLM-style; diminishing returns |

For low-resource extension: ADD 10K-30K to the existing source vocab. Don't remove source vocab.

## Character coverage

`character_coverage`: fraction of training-data characters the tokenizer must include. Lower means rare characters get byte-fallback'd or `<unk>`'d.

| Script | Recommended `character_coverage` | Why |
|---|---|---|
| Latin / Cyrillic / Greek | 0.9999 | Limited character inventory; rare chars likely OCR errors |
| Indic (Devanagari, Tamil, ...) | 0.99999 | Conjuncts + variants are semantically meaningful |
| Han (Chinese) | 0.99999 | 5000+ rare characters carry meaning (especially names) |
| Arabic / Hebrew | 0.99999 | Letter forms + presentation forms |
| Khmer / Myanmar / Tibetan | 0.99999 | Complex sub-script diacritics |

**Lower the coverage and you'll silently drop rare-but-meaningful characters** (names, technical terms, archaic forms).

## Byte fallback

`byte_fallback=True`: any character not in vocab is encoded as its UTF-8 bytes (each byte is a token). Costs more tokens but eliminates `<unk>`.

**ALWAYS ENABLE** for class 0-2 + ideographic / abugida / abjad. See `references/byte_fallback.md` for the full policy.

## Other key params

| Param | Default | Notes |
|---|---|---|
| `split_digits` | true | Split digits to single-token; better for arithmetic |
| `add_dummy_prefix` | true (Latin/Cyrillic) | Adds leading space for word-initial tokens |
| `treat_whitespace_as_suffix` | false | Llama-style; some downstream tasks prefer suffix |
| `normalization_rule_name` | nfkc | Use `identity` if you've handled Unicode upstream (recommended) |
| `pad_id, unk_id, bos_id, eos_id` | 0,1,2,3 | Standard |
| `user_defined_symbols` | [] | Add language tags `<lang_xx>`, special tokens, reserved IDs |
| `required_chars` | "" | Force-include specific characters (e.g., must-have rare names) |
| `max_sentence_length` | 4192 | Increase for long-form training data |
| `shuffle_input_sentence` | true | Better convergence |

## Recommended config templates

### Latin/Cyrillic, class 3+

```yaml
input: training.txt
model_type: unigram
vocab_size: 64000
character_coverage: 0.9999
byte_fallback: true
split_digits: true
add_dummy_prefix: true
normalization_rule_name: identity  # NFC handled upstream
user_defined_symbols: ["<lang_en>", "<lang_de>", "<lang_fr>", "<reserved_0>", "<reserved_1>"]
```

### Han (Chinese, mixed Mandarin+Cantonese)

```yaml
input: training.txt
model_type: unigram
vocab_size: 100000
character_coverage: 0.99999
byte_fallback: true
split_digits: true
add_dummy_prefix: false  # Han is space-less
normalization_rule_name: identity
user_defined_symbols: ["<lang_cmn>", "<lang_yue>"]
```

### Indic (multi-script: Devanagari + Latin code-mix)

```yaml
input: training.txt
model_type: unigram
vocab_size: 80000
character_coverage: 0.99999
byte_fallback: true
split_digits: true
add_dummy_prefix: true
normalization_rule_name: identity
user_defined_symbols: ["<lang_hi>", "<script_deva>", "<script_latn>"]
```

### Class 0-1 (e.g., Inuktitut from scratch)

```yaml
input: training.txt
model_type: unigram
vocab_size: 16000  # smaller — limited data
character_coverage: 0.99999
byte_fallback: true  # MANDATORY
split_digits: true
add_dummy_prefix: false  # polysynthetic — words are huge
treat_whitespace_as_suffix: false
normalization_rule_name: identity
```

## Common mistakes

- **`character_coverage=0.9995` for Han**: drops 5% of characters → drops thousands of distinct chars → name handling broken.
- **`byte_fallback=False` for class 0-2**: OOV cascade in production.
- **No user-defined symbols for language tags**: can't condition multilingual generation cleanly.
- **`vocab_size=16000` on a multilingual extension**: too small; new-language coverage starves.
- **`max_sentence_length` left at default for very long-doc training**: silent truncation.

## Validation

After training:
1. Re-run fertility audit on held-out target text.
2. Verify all language tags / special tokens are encoded as single tokens (not split).
3. Check character coverage on a held-out sample matches training.
4. Round-trip test: encode → decode → string equality on 100 samples.

## See also

- **SentencePiece official docs**: https://github.com/google/sentencepiece
- **Kudo & Richardson (2018)**, *SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing* (EMNLP demo).
- **Kudo (2018)**, *Subword Regularization: Improving Neural Network Translation Models with Multiple Subword Candidates* (ACL).
- **Provilkov et al. (2020)**, *BPE-Dropout: Simple and Effective Subword Regularization* (ACL).
