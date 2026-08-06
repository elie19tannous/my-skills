# Dataset Catalog — Reference

Loaded by `magic-linguistic-corpus` Step 1. Cached snapshot 2026-04-23.

## Major multilingual corpora

| Catalog | Languages | Total size | License | Source | Register | Known issues |
|---|---|---|---|---|---|---|
| **OLDI** (Open Language Data Initiative) | 200+ | varied per lang | mostly CC-BY | https://oldi.org/ | mixed (FLORES-derived + community contributions) | Curated; quality high |
| **CulturaX** | 167 | 6.3T tokens | per-source | https://huggingface.co/datasets/uonlp/CulturaX | web-dominated | mC4 + OSCAR derived; cleaning + dedup applied |
| **MADLAD-400** | 419 | 3T tokens (clean) | per-source | https://huggingface.co/datasets/allenai/MADLAD-400 | web | Cleaner than mC4 for low-resource; per-doc LID |
| **Glot500-c** | 500+ | 700B tokens | per-source | https://huggingface.co/datasets/cis-lmu/Glot500 | mixed inc. Bible-NLP | Designed for 500-language pretrain |
| **mC4** | 101 | varied | ODC-BY | https://www.tensorflow.org/datasets/catalog/c4 | web | Underlies CulturaX; raw |
| **OSCAR** | 168 | per-version | per-source | https://oscar-project.org/ | web | Common Crawl filtered |
| **MaLA-500** | 500+ | per-lang | per-source | https://huggingface.co/datasets/MaLA-LM/mala-corpus | mixed | Curated for MaLA-500 model |
| **Wikipedia dumps** | ~300 (active) | varied | CC-BY-SA | https://dumps.wikimedia.org/ | encyclopedic | Bot-generated for Cebuano/Waray/Volapük (downweight) |
| **Common Crawl** | many (LID-filtered) | varies per snapshot | per-page | https://commoncrawl.org/ | web | Per-page rights uncertain; news commonly disputed |

## Region-specific catalogs

| Region | Catalog | Languages |
|---|---|---|
| Africa | **AfroLM corpus** | 23 African; community-led |
| Africa | **MasakhaNER 2.0** | 21 (NER labeled) |
| Africa | **MAFAND-MT** | 21 (parallel + monolingual) |
| South Asia | **AI4Bharat IndicCorp** | 22 Indic; ~30B tokens |
| South Asia | **Samanantar** | 11 Indic (parallel) |
| SEA | **SEACrowd** | ~700 SEA languages; multi-task |
| SEA | **SEALD** | SEA monolingual |
| Indigenous Americas | **AmericasNLP shared task data** | ~10 (parallel + monolingual) |
| Indigenous Americas | **AILLA archive** | 100+ (community-gated) |
| Endangered global | **ELAR / DELAMAN** | 1000+ (mostly community-gated) |
| Religious | **Bible-NLP** | 1100+ (Bible translations) |
| Speech | **Common Voice** (Mozilla) | ~100 (audio + transcripts) |
| Speech | **OpenSLR** | 200+ (varied) |

## Per-language quick lookup (sample)

| Language | Best mono catalog | Best bitext | Notes |
|---|---|---|---|
| Yoruba (yor) | MADLAD-400 + MasakhaNER + Bible-NLP | FLORES-200 + MAFAND-MT | Class 2-3; tone preservation critical |
| Khmer (khm) | SEACrowd + CulturaX + Wikipedia | FLORES-200 + OPUS | Word-segmentation needed; sparse |
| Inuktitut (iku) | NWT Hansard + community archives | Hansard EN-IU + FLORES (limited) | Class 0-1; community-controlled |
| Quechua (que → quz) | AmericasNLP + AILLA (gated) | AmericasNLP MT shared task | Macrolang; community partnership essential |
| Cantonese (yue) | Hong Kong CC + LIHKG + Wikipedia | OPUS sparse | Many "Cantonese" Wiki pages are written-Mandarin |
| Twi (twi) | AfroLM + MAFAND + Bible-NLP | MAFAND-MT | Class 1-2; tone language |

## Catalog overlap warning

**CulturaX ⊂ MADLAD-400 partial.** Many sources (mC4, OSCAR) appear in both. Naïve union inflates 2-3×. Always dedup AFTER concatenation.

**Glot500-c includes Bible-NLP heavily** for low-resource. Bible % can exceed 60% for some Class 0-1 languages — flag in manifest.

**Wikipedia and Common Crawl overlap.** Wiki appears in CC snapshots; if both are sources, dedup with paragraph-level shingles.

## Refresh procedure

- Catalog landscape changes faster than ML — re-check this reference quarterly.
- New 2026 releases to watch: OLDI growing per WMT cycle; SEACrowd Phase 2; AI4Bharat IndicLLM corpus.
- Pin catalog snapshot dates in your corpus manifest.

## See also

- **Costa-jussà et al. (2022)**, NLLB paper — corpus selection methodology.
- **Kudugunta et al. (2023)**, MADLAD-400 paper.
- **ImaniGooghari et al. (2023)**, Glot500.
- **Bondarenko et al. (2024)**, OLDI shared task findings.
