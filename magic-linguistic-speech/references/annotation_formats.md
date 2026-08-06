# Annotation Formats — Reference

Loaded by `magic-linguistic-speech` Step 1.

## Overview

Field linguistics produces audio + annotation in several formats. Each has its own structure + pre-processing requirements before ingestion into ML pipelines.

| Format | Tool | Use |
|---|---|---|
| **EAF** | ELAN | Time-aligned tiered annotation; multi-tier (transcription, gloss, translation, IPA) |
| **TextGrid** | Praat | Time-aligned interval/point tiers; phonetic-analysis-friendly |
| **FLEx XML** | SIL FieldWorks | Lexical + interlinear-glossed text (IGT) export |
| **SayMore IMDI** | SayMore | Session metadata + media + ELAN integration |
| **Toolbox** | SIL Toolbox (legacy) | Older interlinearized text |
| **OLAC / IMDI metadata** | various | Archive-standard metadata |

## ELAN EAF format

XML-based. Each annotation is a tier with intervals (start/end timestamps) carrying labels.

Common tiers (varies wildly per project):
- `tx` / `transcription` / `tx@xxx` — orthographic transcription.
- `wd` / `words` — word-level segmentation.
- `mb` / `morphemes` — morpheme breakdown.
- `gl` / `gloss` — interlinear gloss (English or pivot language).
- `ft` / `tr` — free translation.
- `ipa` / `phonetic` — IPA transcription.
- `nt` — notes.

**No standardization.** Check tier names per-project. Standardize at ingest.

## Praat TextGrid format

Plain text. Each tier is interval (with text labels) or point (instantaneous).

Common use: phonetic measurement (vowel duration, formant frequencies, pitch tracking). Praat scripts can extract acoustic features.

For ML ingest: TextGrid → Lhotse cut (interval boundaries → supervision spans).

## FLEx FieldWorks XML

Complex schema. Includes:
- Lexicon entries (lexemes, glosses, definitions).
- IGT (interlinear glossed text) — sentence with morpheme alignment + gloss.
- Records, references, taxonomy.

**Critical pre-processing**: many FLEx projects use SIL Private-Use-Area (PUA) characters from legacy SIL fonts. Convert PUA → Unicode at ingest. Mapping tables exist; SIL provides per-font conversion.

Without PUA conversion: downstream Unicode pipelines see unrecognizable bytes; silent corruption.

## SayMore IMDI

Session-level metadata + media file packaging. Used to organize ELAN-annotated audio into archive-ready packages.

For ML: IMDI metadata → corpus-level metadata; underlying ELAN files extracted for content.

## Format-conversion priorities

| Source | Target | Why | Tool |
|---|---|---|---|
| ELAN EAF | Lhotse CutSet | ML ingest standard | Lhotse + custom prep |
| Praat TextGrid | Lhotse CutSet | Same | Lhotse + custom |
| FLEx XML | CoNLL-U or JSONL | ML-readable IGT | LingView, custom |
| SayMore IMDI | Per-component (ELAN extracted) | Get to content | SayMore CLI, custom |

## Tier-naming standardization (recommended)

For new projects + ingest from heterogeneous sources, standardize to:

| Standard tier | Content | Notes |
|---|---|---|
| `transcription_orth` | Orthographic transcription in target language | Always preserve diacritics |
| `transcription_ipa` | IPA transcription (where available) | Validate via ipa_validate |
| `morphemes` | Morpheme-segmented form | One per orthographic word |
| `gloss_en` | English interlinear gloss | One per morpheme |
| `translation_free` | Free translation | One per utterance |
| `notes` | Linguist notes | Free text |

Document the mapping from source-project tier names to standard at ingest.

## See also

- ELAN: https://archive.mpi.nl/tla/elan
- ELAN EAF format docs: https://www.mpi.nl/corpus/manuals/manual-elan.pdf
- Praat: https://www.fon.hum.uva.nl/praat/
- FLEx: https://software.sil.org/fieldworks/
- SayMore: https://software.sil.org/saymore/
- IMDI: https://archive.mpi.nl/forms/imdi/
