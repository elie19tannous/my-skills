# Adapter Patterns — Reference

Loaded by `magic-linguistic-transfer` Step 2.

## The four main approaches

### 1. Continued Pretraining (CP)
- **What**: Continue base-model training on target-language monolingual data.
- **When**: ≥ 1B target tokens + budget for full-model gradient updates.
- **Cost**: Highest. Ballpark: $5K-$50K for 7B model + 1B tokens single-GPU; multi-GPU faster + cheaper per-token.
- **Risk**: Catastrophic forgetting if no source-mix; vocab mismatch if no extension.
- **Best for**: Class 3+ targets with abundant data + close source.

### 2. LoRA / QLoRA / DoRA
- **What**: Low-rank adaptation; freeze base; train rank-N matrices on selected layers.
- **When**: Default for class 1-3 fine-tune. Almost always paired with vocab extension.
- **Cost**: Low. Ballpark: $50-$500 for 7B + 100M tokens single-GPU.
- **Risk**: Rank too low → can't represent adaptation; rank too high → wasted parameters + slower.
- **Best for**: Class 1-3, anything cross-lingual without massive data.

QLoRA: 4-bit quantized base + LoRA. Same recipe, lower memory.
DoRA: decomposes LoRA into magnitude + direction; better than LoRA in many tasks; emerging as default.

### 3. Adapter modules (MAD-X / BAD-X / Houlsby / Pfeiffer)
- **What**: Insert small bottleneck layers; freeze base; train adapter only.
- **When**: Multilingual + multi-task (different language adapters + different task adapters; stack at inference).
- **Cost**: Comparable to LoRA.
- **Risk**: Adapter stacking can be brittle; less ecosystem support than LoRA in 2026.
- **Best for**: Multilingual research + multi-task projects with reusable language adapters.

MAD-X: Modular Adapter Design — separate language + task adapters; popular in pre-LoRA era.
BAD-X: Bilingual Adapter — language pair specific; for MT.

### 4. Full fine-tune
- **What**: Update all parameters.
- **When**: Class 5 only, or when LoRA / CP demonstrably insufficient.
- **Cost**: Same magnitude as continued pretraining.
- **Risk**: Catastrophic forgetting at scale.
- **Best for**: When you have data + budget + need maximum quality on a single language.

## Approach selection matrix

| Target class | Parallel data | URIEL to best source | Approach |
|---|---|---|---|
| 0-1 | < 10K | any | HyperOfa vocab extension + LoRA on multilingual base |
| 1-2 | 10K-100K | < 0.4 | OFA + LoRA r=16-32 |
| 1-2 | 10K-100K | 0.4-0.6 | OFA + LoRA r=32-64 |
| 1-2 | 10K-100K | > 0.6 | HyperOfa + LoRA r=32+ on multilingual base |
| 2-3 | 100K-1M | < 0.4 | CP + LoRA |
| 2-3 | 100K-1M | > 0.6 | OFA + LoRA r=32-64 |
| 3-4 | 1M-10M | any | CP + LoRA OR full fine-tune |
| 5 | abundant | any | Standard full fine-tune |

## Common method-mismatches

| Mismatch | Why it's bad |
|---|---|
| Continued pretraining + < 100M target tokens | Overfits + forgets source |
| Full fine-tune + LoRA-only data budget | Wastes parameters; LoRA was sufficient |
| LoRA r=4 + URIEL > 0.6 | Rank insufficient for adaptation |
| HyperOfa + full fine-tune without LoRA | Wastes hyper-network init |
| FOCUS + LoRA without CP | FOCUS designed for CP; just OFA otherwise |
| Adapter stacking + single-language single-task | Over-engineering; LoRA simpler |

## See also

- **Pfeiffer, J., et al.** (2020). *MAD-X: An Adapter-Based Framework for Multi-Task Cross-Lingual Transfer*. EMNLP.
- **Hu, E., et al.** (2021). *LoRA: Low-Rank Adaptation of Large Language Models*. ICLR.
- **Dettmers, T., et al.** (2023). *QLoRA: Efficient Finetuning of Quantized LLMs*. NeurIPS.
- **Liu, S.-Y., et al.** (2024). *DoRA: Weight-Decomposed Low-Rank Adaptation*. ICML.
- **Parović, M., et al.** (2023). *Cross-Lingual Transfer with Target-Language-Ready Task Adapters*. ACL findings (BAD-X).
