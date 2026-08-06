# Vocabulary Extension Methods — Reference

Loaded by `magic-linguistic-tokenize` Step 2.

## The four methods

| Method | When to use | Cost | Quality | Reference |
|---|---|---|---|---|
| **FOCUS** | Same script + high token overlap (Latin → Latin) | Low | Good for similar pairs | Dobler & de Melo (2023) |
| **OFA** | Different script + parallel data (English → Hindi) | Medium | Good general default | Liu et al. (2024) |
| **HyperOfa** | Different script + minimal data + typologically distant | Medium-high | Best for class 0-1 | Wang et al. (2025) |
| **Full retrain** | No usable base + budget for re-pretraining | Very high | Best ceiling but rarely worth it | — |

## Method 1: FOCUS (Fast Overlapping-vocabulary-token Cosine-similarity Selection)

**Idea**: identify tokens in the source vocabulary that already cover the target language well; only add new tokens for genuinely new orthography.

**When**: source and target share script + significant character overlap. Examples:
- English-trained tokenizer extended to French, Spanish, German.
- Russian-trained extended to Ukrainian, Bulgarian.
- Mandarin-trained extended to Cantonese (Han characters mostly shared).

**Procedure**:
1. Train a small SentencePiece model on target-only data.
2. For each new token, check if a source token (or short combination of source tokens) already covers it.
3. Add only tokens that don't have good coverage in source.
4. Initialize new-token embeddings as weighted sum of overlapping source tokens.

**Typical cost**: 100M-1B target tokens for embedding initialization; LoRA fine-tune adapts.

**Failure mode**: assumes high overlap. If source-target overlap is low (< 30% character coverage), FOCUS adds too many tokens AND under-initializes them — LoRA can't catch up cheaply.

## Method 2: OFA (One For All)

**Idea**: project new-token embeddings into source's embedding space using parallel data.

**When**: cross-script transfer with parallel data available. Examples:
- English → Hindi (parallel via OPUS / NLLB).
- English → Yoruba (parallel via FLORES + Bible).
- English → Vietnamese.

**Procedure**:
1. Train target SentencePiece on monolingual target.
2. Use parallel data to compute target-source token alignments.
3. Initialize new-token embeddings as weighted average of aligned source tokens.
4. LoRA fine-tune on target monolingual + parallel.

**Typical cost**: 100K-10M parallel pairs + 100M-1B target tokens monolingual. LoRA r=16-32.

**Failure mode**: needs parallel data. If you have < 100K pairs for the target, OFA initialization is noisy → worse than HyperOfa.

## Method 3: HyperOfa

**Idea**: train a small hyper-network that predicts new-token embeddings from token surface form. No parallel data required.

**When**: minimal target data, typologically distant from source, want to extend without expensive parallel data prep. Examples:
- English → Inuktitut (no useful parallel; very distant typology).
- English → Cherokee (limited data).
- Class 0-1 languages generally.

**Procedure**:
1. Train target SentencePiece on monolingual target.
2. Train hyper-network on source (token surface → embedding) using source's full vocab as supervision.
3. Run hyper-network on target's new tokens to predict embeddings.
4. LoRA fine-tune on target monolingual.

**Typical cost**: 10M-100M target tokens. LoRA r=16.

**Failure mode**: hyper-network quality varies; less proven than OFA for high-resource targets. Use when you can't use OFA.

## Method 4: Full Retrain

**When**: class 0-1 + no usable source base + budget exists. Almost never the right answer.

**Cost**: pretrain a tokenizer + (re)pretrain the base model. For 7B params: $100K-1M+. For 70B: $5M+.

**Alternative**: use a multilingual base (NLLB-200, BLOOM, mBART) that already includes the target → switch to OFA/HyperOfa from there.

## Decision flow

```
Fertility audit triggers extension?
├── NO → no action
└── YES
    ├── Is the target Joshi class 5 with English-base? → FOCUS sufficient
    ├── Is parallel data ≥ 100K pairs? → OFA
    ├── Is parallel data < 100K?
    │   ├── Is target typologically close to a multilingual-base language? → switch base + OFA from there
    │   └── Else → HyperOfa
    └── Is target class 0 + no usable multilingual base? → consider Full Retrain (rare)
```

## Hyperparameter cheat-sheet

| Method | Source-vocab-keep | New-vocab size | LoRA r | LoRA alpha | Steps |
|---|---|---|---|---|---|
| FOCUS | 100% (don't remove source) | 5K-15K | 16 | 16 | 1-3K |
| OFA | 100% | 10K-30K | 16-32 | 32 | 5-15K |
| HyperOfa | 100% | 10K-30K | 16 | 16 | 10-20K |

## Common mistakes

- **Removing source-vocab tokens to make room for target tokens.** Catastrophic forgetting of source-language capability. Always keep all source tokens; only ADD.
- **Using OFA without checking parallel-data quantity.** < 100K pairs → noisy initialization.
- **LoRA rank too low** for typologically distant pairs (Inuktitut from English with rank 4): rank ≥ 16 is the floor.
- **LoRA fine-tune on target without monolingual pretraining.** Short LoRA on small parallel only over-fits the parallel distribution; underperforms.
- **Skipping the fertility re-audit AFTER extension.** Target fertility should drop to within 1.5× of English baseline; if not, the extension didn't take.

## See also

- **Dobler & de Melo (2023)**, *FOCUS: Effective Embedding Initialization for Monolingual Specialization of Multilingual Models* (EMNLP).
- **Liu et al. (2024)**, *OFA: A Framework of Initializing Unseen Subword Embeddings for Efficient Large-scale Multilingual Continued Pretraining* (NAACL).
- **Wang et al. (2025)**, *HyperOfa: Hypernetwork-based Vocabulary Adaptation for Cross-Lingual Transfer* (preprint).
- **Pfeiffer et al. (2020)**, *MAD-X: An Adapter-Based Framework for Multi-Task Cross-Lingual Transfer* (EMNLP).
- **Hu et al. (2021)**, *LoRA: Low-Rank Adaptation of Large Language Models* (ICLR).
