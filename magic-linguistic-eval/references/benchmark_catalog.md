# Benchmark Catalog — Reference

Loaded by `magic-linguistic-eval` Step 2.

## MT benchmarks

| Benchmark | Languages | Released | Notes |
|---|---|---|---|
| **FLORES-200 / FLORES+** | 200+ | 2022-07; OLDI maintained | Sentence-level MT; in many pretrain mixes |
| **NTREX-128** | 128 | 2022-11 | Cleaner contamination profile than FLORES |
| **OPUS test sets** | many | rolling | Domain-specific |
| **WMT shared task data** | varies per year | annual | News-domain dominant |
| **MAFAND-MT** | 21 African | 2022 | African focus |
| **AmericasNLP MT shared task** | ~10 Indigenous Americas | annual | |
| **IN22** | Indic (22 langs) | 2023 | AI4Bharat; per-direction |
| **SEACrowd MT subset** | SEA | 2025 | Newer |

## Reading comprehension

| Benchmark | Languages | Notes |
|---|---|---|
| **Belebele** | 122 | Multiple-choice; 2023-08 release |
| **TyDi-QA** | 11 | Information-seeking QA |
| **XQuAD** | 10 | English SQuAD translated |
| **MLQA** | 7 | Multi-language QA |

## NER

| Benchmark | Languages | Notes |
|---|---|---|
| **MasakhaNER 2.0** | 21 African | Community-built |
| **WikiAnn** | ~280 | Auto-generated; quality varies |
| **CoNLL-2003** | 4 (en, de, es, nl) | Classic English-NER baseline |
| **OntoNotes** | 3 (en, ar, zh) | Genre-annotated |

## Sentiment

| Benchmark | Languages | Notes |
|---|---|---|
| **AfriSenti** | 14 African | 2023 |
| **IndicSenti** | Indic | |
| **SemEval per-year** | varies | Cross-lingual sentiment subtasks |

## General-purpose multilingual

| Benchmark | Languages | Notes |
|---|---|---|
| **XNLI** | 15 | Cross-lingual NLI |
| **BIG-bench** subset | 50+ for some tasks | Grouped tasks |
| **MEGA** | 70 | Multilingual eval Africa-focused |
| **BUFFET** | 56 | Few-shot multilingual |
| **AfroBench** | 64 African | 15 tasks; 2024-12 release |
| **IndicXTREME** | 22 Indic | Multi-task |
| **SEACrowd** | ~700 SEA | Multi-task; v2 in 2025 |

## Speech

| Benchmark | Languages | Notes |
|---|---|---|
| **Common Voice** | ~100 | Crowd-sourced; varies in quality |
| **OpenSLR** | 200+ | Various sources |
| **VoxPopuli** | 24 | EU parliament |
| **Multilingual LibriSpeech** | 8 | High-quality MLS |
| **MMS-FLEURS** | 102 | MMS eval set |

## Per-class benchmark recommendations

| Joshi class | Default MT benchmark | Default NER | Default reading-comp |
|---|---|---|---|
| 0 | none → custom held-out | community-built | none → custom |
| 1 | NTREX subset | community-built | none |
| 2 | NTREX + AfroBench / SEACrowd | MasakhaNER / WikiAnn | Belebele if covered |
| 3 | NTREX + region | region-specific + WikiAnn | Belebele |
| 4 | NTREX + FLORES (with contamination caveat) | OntoNotes / region | Belebele + region |
| 5 | FLORES + NTREX + WMT | WikiAnn + custom | Belebele + custom |

## Refresh

- FLORES+: OLDI manages; quarterly minor updates.
- NTREX: stable since 2022-11.
- Belebele: stable since 2023-08.
- AfroBench / SEACrowd: rapid annual updates.

## See also

- **Costa-jussà et al.** (2022). NLLB / FLORES-200 paper.
- **Bandarkar, L., et al.** (2024). *Belebele Benchmark*. ACL.
- **Adelani, D. I., et al.** (2024). MasakhaNER 2.0; AfroBench.
- **Nadeem, F., et al.** (2024). SEACrowd / IndicXTREME papers.
- DISRPT, OLDI, WMT, AmericasNLP yearly findings.
