# UD Treebanks — Reference

Loaded by `magic-linguistic-syntax` Step 1.

## What UD is

Universal Dependencies (UD) is a cross-lingual treebank framework. Same annotation guidelines across 100+ languages. https://universaldependencies.org/

Format: CoNLL-U files with one token per line, columns for ID, FORM, LEMMA, UPOS (universal POS), XPOS (language-specific POS), FEATS (morphological features), HEAD, DEPREL, DEPS, MISC.

## Treebank size tiers (snapshot 2026-04-23)

| Size | Training viable? | Examples |
|---|---|---|
| > 100K sentences | Yes | English-EWT, Czech, Russian, German |
| 10K-100K | Yes | Spanish, French, Polish, Tamil, Vietnamese, Indonesian |
| 1K-10K | Marginal | Yoruba, Hindi, Hungarian, many Slavic |
| PUD test only (~1K) | NO — eval only | many Class 1-2 languages |
| Absent | n/a | many Class 0-1 |

## Per-language quick lookup

| Language | UD treebanks | Total size | Usable for training |
|---|---|---|---|
| English | EWT, GUM, ParTUT, LinES | 200K+ | YES |
| Spanish | AnCora, GSD, PUD | 50K+ | YES |
| Mandarin | GSD, GSDsimp, HK, PUD, CFL | 30K+ | YES |
| Russian | SynTagRus, GSD, Taiga, PUD | 100K+ | YES |
| Vietnamese | VTB | 12K | YES |
| Tamil | TTB | 7K | Marginal |
| Hindi | HDTB, PUD | 17K | YES |
| Yoruba | YTB | 100 sentences (?!) | NO |
| Khmer | none | 0 | NO |
| Twi | none | 0 | NO |
| Inuktitut | IUIT | 1K | NO (treat as eval) |
| Cherokee | none | 0 | NO |
| Quechua | none (some experimental) | 0 | NO |
| Cantonese | HK | 1K (PUD-style) | NO (eval only) |
| Swahili | none (in development) | 0 | NO |
| Amharic | ATT | 1K | NO (eval only) |

## When no UD treebank exists

Cross-lingual zero-shot is the only option. Use:
- Trankit / stanza pretrained model with a typologically-close source.
- Document this clearly in eval (zero-shot ≠ fine-tuned).

## When only PUD-style test exists

Use as **eval-only**. Fine-tuning on PUD = leaked eval = published-paper retraction risk.

## Refresh

UD releases annually (May, around v2.X+1). Treebanks added/updated continuously between releases. Always pin a UD version in your workspace.

## Aggregator services

- `udapi`: Python library for UD data access. https://udapi.github.io/
- `pyconll`: alternative parser.
- HuggingFace `universal_dependencies` dataset: aggregated across versions.

## Common UD pitfalls

- Annotation conventions differ for some languages (Bantu noun classes, switch reference).
- Treebanks for the same language can differ in domain; pick by intended use.
- Train/dev/test splits in different treebanks have different conventions.
- UD v2.0 → v2.5 → v2.10 annotation changes (especially copula, MWE handling).

## See also

- **Nivre, J., et al.** (2020). *Universal Dependencies v2: An Evergrowing Multilingual Treebank Collection*. LREC.
- **Zeman, D., et al.** (2018). *CoNLL 2018 Shared Task: Multilingual Parsing from Raw Text to Universal Dependencies*. CoNLL.
- UD site: https://universaldependencies.org/
