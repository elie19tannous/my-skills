---
name: magic-linguistic-speech
description: Bridge field-linguistics annotation (ELAN, Praat, FLEx, SayMore) and audio data into ML pipelines (Lhotse, ESPnet, k2/icefall, MMS, Whisper). G2P / IPA workflows; low-resource ASR / TTS recipe selection. Use whenever the user mentions ELAN, EAF, Praat, TextGrid, FLEx, SayMore, Lhotse, CutSet, ESPnet, k2, icefall, MMS, Whisper, NeMo, SpeechBrain, G2P, grapheme-to-phoneme, IPA, phonetic transcription, low-resource ASR, low-resource TTS, oral history, field recordings, or asks how to ingest community-annotated audio into a model. Routed by magic-linguistic-orchestrator in the Analyze phase whenever oral / spoken data is involved.
license: Apache-2.0
compatibility: Python 3.12+
metadata:
  domain: linguistics
  complexity: medium
  requires_llm: false
  phase: 3
  supports_pipeline: true
  supports_generation: false
  entry_point: false
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - linguistics
  - speech
  - asr
  - tts
  - ipa
  - g2p
  - lhotse
  - espnet
  - mms
  - low-resource
  dependencies: []
  scripts:
  - scripts/ipa_validate.py
  - scripts/lhotse_recipe_advisor.py
---

## When to Use

- Ingesting field-recorded audio + linguistic annotation (ELAN, Praat, FLEx, SayMore) into ML pipelines.
- Choosing G2P (grapheme-to-phoneme) approach for the target language.
- Selecting low-resource ASR (MMS / Whisper / fine-tune).
- IPA validation in transcription pipelines.
- Building Lhotse CutSet from heterogeneous community-annotated sources.
- Bridging endangered-language oral data into TTS / ASR research.

**When NOT to use:** purely text data → not speech-relevant. Pure tokenizer audit → `magic-linguistic-tokenize`. Annotation methodology → `magic-linguistic-annotate`.

## The Knowledge Engineers Routinely Miss

1. **ELAN tier-naming conventions vary across community projects.** One project uses tier "ipa" for IPA transcription; another uses "phonetic"; another "tx@en"+lang-suffix. Standardize at ingest, not at downstream consumption.

2. **FLEx FieldWorks XML often uses SIL PUA (Private Use Area) characters from older fonts.** Pre-Unicode legacy. Convert to Unicode at ingest or downstream tools choke silently.

3. **Lhotse CutSet** (a "cut" = audio + supervisions + features) is the standard 2026 representation. ESPnet, k2/icefall, SpeechBrain, NeMo all consume it. Build pipelines that produce CutSets, not bespoke formats.

4. **MMS (Meta Massively Multilingual Speech) covers 1107 languages**. Whisper covers ~99 (with varying quality). For class 0-2 languages: MMS is the floor. For class 3-5: Whisper or fine-tuned ASR.

5. **G2P for low-resource: WikiPron is the best free crowd-sourced G2P** dataset. Per-language IPA conventions vary (especially tone marking). Build per-language G2P from WikiPron + community contribution.

6. **Tone preservation in transcription pipelines**: many community ASR pipelines silently strip diacritics. For tone languages (Yoruba, Mandarin, Vietnamese, Hausa), build pipeline that REJECTS diacritic-stripped input. Validate with IPA-validator.

7. **DELAMAN archive integration** (ELAR, AILLA, PARADISEC, DoBeS): different metadata schemas. SayMore IMDI / OLAC are standardization targets. Field projects often export bespoke; ingest needs schema mapping.

8. **TTS for low-resource with limited audio**: VITS or Tacotron2 fine-tune on ~5 hours can produce intelligible output; below 1 hour usually not viable.

## Workflow

### Step 1 — Identify input format

**MANDATORY READ** [`references/annotation_formats.md`](references/annotation_formats.md).

Use `scripts/lhotse_recipe_advisor.py`:
- Per-input-format: ELAN EAF, Praat TextGrid, FLEx XML, SayMore IMDI, custom CSV.
- Recommended Lhotse ingest pattern.
- Pre-processing requirements (PUA → Unicode, tier-name normalization).

### Step 2 — G2P / IPA setup

**MANDATORY READ** [`references/g2p_ipa.md`](references/g2p_ipa.md).

For ASR / TTS / pronunciation lexicon:
- Identify per-language IPA convention (tone marking, vowel-length notation).
- Recommend G2P resource: WikiPron baseline + community refinement.
- Use `scripts/ipa_validate.py` to validate transcription IPA strings against per-language inventory.

### Step 3 — ASR / TTS tool selection

**MANDATORY READ** [`references/asr_tts_recipes.md`](references/asr_tts_recipes.md).

| Class | ASR primary | ASR fallback | TTS |
|---|---|---|---|
| 0-2 | MMS (1107-lang) | Whisper-large + fine-tune | VITS / Tacotron2 fine-tune (≥ 5 hr audio) |
| 3-4 | Whisper-large fine-tune | MMS | VITS / FastSpeech2 |
| 5 | Whisper-large or commercial | n/a | XTTS / commercial |

### Step 4 — Lhotse pipeline

**MANDATORY READ** [`references/lhotse_pipeline.md`](references/lhotse_pipeline.md).

Lhotse CutSet is the canonical representation in 2026:
- Cut = audio + supervisions (transcription, speaker, etc.) + features (Mel-spec, etc.).
- Recipes: per-corpus prep scripts in `lhotse/recipes/`.
- Custom recipes for community-annotated data: ingest tier → supervision; align via Vad / VAD-CTC.

### Step 5 — Output speech plan + hand off

```markdown
## Speech Plan: <Target Language>

**Input format(s):** ELAN EAF | TextGrid | FLEx XML | SayMore IMDI | other
**Pre-processing:** PUA→Unicode | tier-name normalization | diacritic preservation
**G2P approach:** WikiPron baseline | per-language custom | ...
**ASR primary:** MMS | Whisper-fine-tune | ...
**TTS approach:** VITS-fine-tune (~N hr audio needed) | ... | not viable (insufficient audio)
**Lhotse recipe:** <existing | custom>
**IPA validation:** required (tone language)
**Hand-off:** magic-linguistic-ethics (community-controlled audio); magic-linguistic-eval (ASR/TTS metrics)
```

## Anti-patterns (NEVER do)

- **NEVER** strip diacritics in transcription pipelines for tone languages. Tone marks are semantic.
- **NEVER** ingest FLEx XML without PUA → Unicode normalization. Silent corruption.
- **NEVER** assume ELAN tier names are standardized. Per-project audit is required.
- **NEVER** use Whisper for class 0-1 — MMS coverage is broader (1107 vs 99 languages).
- **NEVER** train TTS on < 1 hour of audio. Output will be unusable.
- **NEVER** ingest community-controlled archive data (AILLA, ELAR, PARADISEC) without ethics routing — many archives are FPIC-restricted.
- **NEVER** use Whisper-large output as gold — it has known per-language failure modes (especially tone-stripping).
- **NEVER** skip IPA validation when constructing pronunciation lexicons. Invalid IPA breaks G2P training.

## Edge Cases

- **Mixed-language oral recordings** (code-switched conversations): per-segment LID + per-language ASR.
- **Heavily accented / dialectal audio**: standard ASR underperforms; consider per-dialect fine-tune.
- **Sparse audio + dense annotation** (few hours, lots of glosses): use annotation for G2P + lexicon, not direct ASR training.
- **Endangered-language singing / chanting**: standard ASR/TTS not designed for; flag.
- **Multi-speaker recordings without diarization**: VAD + diarization pipeline first; then per-speaker ASR.
- **Audio quality issues** (field recordings often noisy): denoise (e.g., Demucs, Facebook DNS) before ASR.

## Pinned recipe stubs (per Q8 resolution)

Two minimal recipe templates ship in `references/lhotse_pipeline.md`:
1. **MMS fine-tune skeleton** — Hugging Face `transformers` + MMS-1B; pinned to specific snapshot.
2. **Lhotse CutSet from ELAN EAF** — code template for ELAN-format ingestion.

Both pinned to library versions current as of 2026-04-23. Refresh procedure documented in `canonical_sources.md`.

## Output Format

```markdown
## Speech Analysis: <Target Language>

**Input format diagnosis:** ...
**Pre-processing required:** ...
**G2P approach:** ...
**ASR / TTS recommendation:** ...
**Lhotse pipeline:** ...
**IPA validation:** required | optional
**Anti-patterns to avoid:** ...
**Hand-off:** magic-linguistic-ethics; magic-linguistic-eval; magic-linguistic-corpus
```
