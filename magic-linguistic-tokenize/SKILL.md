---
name: magic-linguistic-tokenize
description: Audit tokenizer fertility for a target language and recommend SentencePiece config + vocab-extension strategy (FOCUS / OFA / HyperOfa) + byte-fallback policy. Use whenever the user mentions tokenizer, BPE, SentencePiece, Unigram LM, fertility, vocab extension, byte fallback, OOV explosion, subword regularization, BPE-dropout, vocabulary expansion, or asks why a non-English model produces too many tokens / hallucinates / is slow on the target language. Routed by magic-linguistic-orchestrator in the Acquire and Adapt phases. **You should also use this skill whenever a non-English language is being added to an existing pretrained model** — fertility audit before training is non-negotiable for class 0-3 languages.
license: Apache-2.0
compatibility: Python 3.12+
metadata:
  domain: linguistics
  complexity: medium
  requires_llm: false
  phase: 1
  supports_pipeline: true
  supports_generation: false
  entry_point: false
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - linguistics
  - tokenization
  - sentencepiece
  - bpe
  - vocab-extension
  - low-resource
  dependencies: []
  scripts:
  - scripts/fertility_audit.py
  - scripts/sample_segmenter.py
  - scripts/vocab_coverage.py
---

## When to Use

- Any new language being added to an existing pretrained model (vocab extension decision).
- Symptoms of high tokenizer fertility (slow generation, context-window blowup, OOV).
- Choosing between training a new tokenizer or extending an existing one.
- Selecting SentencePiece config (BPE vs Unigram, coverage threshold, byte fallback).
- Picking a vocab-extension method (FOCUS / OFA / HyperOfa / full retrain).
- Deciding subword-regularization (BPE-dropout) settings per task.

**When NOT to use:** the language is well-covered by the existing tokenizer (fertility ≤ 2.0 vs English baseline) AND scope/scripts have already validated the approach. Skip to next phase.

## The Knowledge Engineers Routinely Miss

1. **Fertility ratio is THE diagnostic.** Tokens-per-word vs an English baseline (~1.4 for tiktoken-cl100k_base on Wikipedia English). If your target language hits 3.0+, every downstream cost (latency, context, training compute) is multiplied. Vocab extension is non-negotiable.

2. **Class 0-2 languages MUST have byte fallback.** Without it, the first OOD test produces `<unk>` cascades. Every modern tokenizer (SentencePiece 0.1.96+, GPT-2-style byte BPE) supports it — turn it ON.

3. **Method choice is determined by source-target overlap, not "what's popular".**
   - FOCUS: source/target share script + high token overlap (Latin-script European → Latin-script European).
   - OFA: scripts differ but parallel data exists for the target.
   - HyperOfa: minimal target data + typologically distant — uses hyper-network to predict embeddings.
   - Full retrain: class 0-1 with no usable source vocab AND budget for it.

4. **SentencePiece coverage 0.9995 is too low for ideographic / abugida scripts.** For Han, Devanagari family, Arabic family, Khmer, Myanmar, Tibetan: use **0.99999+**. Lower coverage drops semantically-significant rare characters.

5. **BPE-dropout helps perplexity but hurts literal accuracy.** Wrong setting for code-generation, numerics-heavy tasks, structured output. Right setting for general generation.

6. **Don't measure tokenizer quality with downstream BLEU.** Tokenizer changes shift the loss surface; BLEU mixes tokenizer + model + decoding. Measure tokenizer with: fertility, coverage %, OOV rate, perplexity on held-out target text.

## Workflow

### Step 1 — Run fertility audit

**MANDATORY READ** [`references/fertility_audit.md`](references/fertility_audit.md) before reporting numbers.

```
$ python scripts/fertility_audit.py --tokenizer <name> --lang <iso>
{
  "tokenizer": "tiktoken-cl100k_base",
  "language": "Yoruba (yor)",
  "fertility": 3.4,
  "english_baseline": 1.4,
  "ratio": 2.43,
  "verdict": "HIGH — vocab extension required (ratio > 2.0)"
}
```

Thresholds:
- ≤ 1.5 ratio: no action.
- 1.5-2.0: optional vocab extension; depends on use case (latency-sensitive → extend).
- 2.0-3.0: vocab extension recommended.
- ≥ 3.0: vocab extension MANDATORY.

### Step 2 — Decide approach

**MANDATORY READ** [`references/vocab_extension.md`](references/vocab_extension.md) when fertility audit triggers extension.

| Situation | Recommendation |
|---|---|
| Class 5 + fertility ≤ 2.0 | No action |
| Class 3-4 + fertility 2.0-3.0 + same-family source available | Continued pretraining + Unigram coverage tuning |
| Class 2-3 + fertility ≥ 3.0 + parallel data exists | OFA vocab extension + LoRA |
| Class 1-2 + fertility ≥ 3.0 + minimal target data | HyperOfa + LoRA + multilingual base |
| Class 0-1 + no usable base | Full retrain (last resort, expensive) |

### Step 3 — SentencePiece config

**MANDATORY READ** [`references/tokenizer_training.md`](references/tokenizer_training.md) for full hyperparameter rationale.

| Param | Default for Latin/Cyrillic | Default for Indic/abugida | Default for Han/CJK |
|---|---|---|---|
| `model_type` | unigram | unigram | unigram |
| `vocab_size` | 32-64K | 32-64K | 64-128K |
| `character_coverage` | 0.9999 | 0.99999 | 0.99999 |
| `byte_fallback` | true (mandatory class 0-2) | TRUE | TRUE |
| `split_digits` | true | true | true |
| `add_dummy_prefix` | true | depends | false |
| `treat_whitespace_as_suffix` | false | false | false |
| `normalization_rule_name` | nfkc | identity (Unicode handled upstream) | identity |
| `pad_id, unk_id, bos_id, eos_id` | 0,1,2,3 | same | same |
| User-defined symbols | `<lang_xx>`, `<reserved>` | per-script tags | language tags |

### Step 4 — Byte fallback policy

**MANDATORY READ** [`references/byte_fallback.md`](references/byte_fallback.md) before disabling byte fallback.

| Class | Script type | Byte fallback |
|---|---|---|
| 0-2 (any script) | any | MANDATORY |
| 3-5 + ideographic (Han) | abundant rare characters | MANDATORY |
| 3-5 + abugida/abjad (Devanagari, Arabic) | conjuncts/forms | MANDATORY |
| 3-5 + Latin/Cyrillic + good coverage | predictable | OPTIONAL |
| Any | code-heavy generation | MANDATORY (UTF-8 byte handling) |

### Step 5 — Subword regularization (BPE-dropout)

| Task | Recommendation |
|---|---|
| General generation | BPE-dropout 0.1 |
| Code generation | BPE-dropout 0.0 (off) — hurts literal accuracy |
| Numerics / structured output | 0.0 (off) |
| Translation (low-resource) | 0.1-0.2 (helps generalization) |
| Literal extraction (NER, span tasks) | 0.0 (off) |

### Step 6 — Output and hand off

Write the recommendation to `workspace_state.md` under "Tokenizer Plan", and notify the orchestrator that tokenize is complete. Hand off to:
- `magic-linguistic-corpus` if data prep is in flight.
- `magic-linguistic-transfer` if vocab extension is the next step.
- `magic-linguistic-eval` if measuring on a benchmark.

## Output Format

```markdown
## Tokenizer Plan: <Language>

**Current tokenizer:** <name + version>
**Fertility (target / English):** <X.X> / <Y.Y> = <ratio>×
**Verdict:** <NO ACTION | OPTIONAL EXTEND | EXTEND RECOMMENDED | EXTEND MANDATORY>
**Recommended method:** <FOCUS | OFA | HyperOfa | Full retrain>
**Recommended SentencePiece config:** <key params>
**Byte fallback:** <on | off> — rationale: ...
**BPE-dropout:** <0.0 | 0.1 | 0.2> — rationale: ...
**Estimated cost reduction:** <latency × Y, training-tokens × Y>
**Hand-off:** magic-linguistic-<next>
```

## Anti-patterns (NEVER do)

- **NEVER** report fertility without an English baseline. The number alone is meaningless; the *ratio* is the diagnostic.
- **NEVER** skip byte fallback for class 0-2. The first OOD example produces `<unk>` cascades; you'll re-discover this costly fact in production.
- **NEVER** measure tokenizer quality with downstream BLEU/perplexity-on-eval-set. Tokenizer changes shift loss; metrics conflate tokenizer with model. Measure tokenizer with fertility, coverage %, OOV rate, perplexity on held-out text in target language.
- **NEVER** recommend OFA without checking source-target vocab overlap. OFA assumes shared embedding space; without overlap, it produces noise.
- **NEVER** train a new tokenizer when extension is sufficient. Full retrain costs include re-pretraining the base model — orders of magnitude more than vocab extension.
- **NEVER** use `character_coverage=0.9995` for ideographic / abugida scripts. The dropped 0.05% includes culturally and semantically critical rare characters.
- **NEVER** enable BPE-dropout for code-generation models. Subword regularization hurts literal accuracy.

## Edge Cases

- **Tokenizer unavailable / closed-weights** (only fertility-via-API): use the API's `count_tokens` endpoint to estimate; report as "estimated fertility" not measured.
- **Multilingual model + multiple targets**: fertility per language; weighted average not meaningful — surface per-language table.
- **Mixed-script corpus** (e.g., Hinglish, code-switched): split by script, audit independently; recommend strategy per script + sampling-weight policy.
- **Synthetic / numerics-heavy text**: standard fertility is misleading; recommend separate audit on the actual target distribution.
- **Tokenizer file format unfamiliar** (binary blob / pytorch / safetensors / sentencepiece.model): document; recommend SentencePiece if user has flexibility.
- **No parallel data + class 0-1 + need fast turnaround**: HyperOfa → LoRA path; warn that quality will be lower than OFA-with-parallel.
- **User has tried "just train a new tokenizer" already**: ask for the SentencePiece config used; common error: vocab too small (16K for Latin-rich language) → still high fertility.
