# Fine-Tuning Recipes — Reference

Loaded by `magic-linguistic-transfer` Step 3 (LoRA config) and Step 6 (tool selection).

## Tool comparison (snapshot 2026-04-23)

| Tool | Strengths | Weaknesses | Best for |
|---|---|---|---|
| **Unsloth** | 2× faster QLoRA on single GPU; great defaults; growing model support | Multi-GPU support limited; less complex multilingual sampling | Single-GPU QLoRA; speed priority |
| **LLaMA-Factory** | Multi-GPU; complex sampling weights; multilingual recipes; web UI | Slower than Unsloth on single GPU | Multi-GPU multilingual |
| **Axolotl** | YAML config; ergonomic; community recipes | Slower than Unsloth | YAML-config users; reproducibility |
| **HuggingFace PEFT** | Lowest level; full control; widely supported | Manual config; no defaults | When other tools don't fit |
| **HF Adapters library** | MAD-X / BAD-X stacking | Less common in 2026; LoRA ecosystem larger | Adapter-stack research |
| **TRL (HF)** | Built on PEFT; SFT/DPO/PPO trainers | Less low-resource specific | RL fine-tunes (DPO etc.) |

**Default recommendation hierarchy:**
1. Unsloth for single-GPU QLoRA on supported models.
2. LLaMA-Factory for multi-GPU or complex multilingual sampling.
3. Axolotl for YAML-config preference.

## LoRA config by URIEL distance

```python
def lora_config_for_distance(uriel: float) -> dict:
    if uriel < 0.2:
        return {"r": 8, "alpha": 16, "target_modules": ["q_proj", "v_proj"], "dropout": 0.05}
    if uriel < 0.4:
        return {"r": 16, "alpha": 32, "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"], "dropout": 0.05}
    if uriel < 0.6:
        return {"r": 32, "alpha": 64, "target_modules": "all-linear", "dropout": 0.05}
    if uriel < 0.8:
        return {"r": 64, "alpha": 128, "target_modules": "all-linear", "dropout": 0.05, "modules_to_save": ["embed_tokens"]}
    return {"r": 128, "alpha": 256, "target_modules": "all-linear", "dropout": 0.05, "modules_to_save": ["embed_tokens", "lm_head"]}
```

`all-linear` = `["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]` for Llama-style.

## Sampling-weight tuning (multilingual fine-tune)

When training on N languages simultaneously:

```
prob(language i) = (n_i)^α / sum_j (n_j)^α
```

- α=1 → proportional to data size; high-resource dominates.
- α=0.5 → balanced; mid-low-resource get more share.
- α=0.3 → strongly upweight low-resource.
- α=0 → uniform; English-equal-to-Yoruba.

**Default for multilingual cross-lingual training**: α=0.3-0.5.

## Catastrophic forgetting: source-mix ratio

| Source-mix ratio | Behavior |
|---|---|
| 0% (pure target) | Heavy forgetting; English perplexity rises 20-50% |
| 10% | Moderate prevention; English perplexity rises 5-10% |
| 20% | Strong prevention; English perplexity stable; target gain slightly slower |
| 50% | Over-protection; target gain very slow; usually unnecessary |

Default: **15-20%** for cross-lingual cross-task.

## Common training recipes

### Class 1-2 + LoRA + multilingual base
```yaml
base_model: facebook/nllb-200-1.3B  # or Llama-3-8B + extended vocab
quantization: bf16  # 4-bit if memory tight (QLoRA)
lora:
  r: 32
  alpha: 64
  target_modules: all-linear
  dropout: 0.05
training:
  data_mix:
    target_lang: 0.80
    source_lang: 0.20
  sampling_alpha: 0.5
  learning_rate: 1e-4
  batch_size: 8 (effective 32 via grad accum)
  warmup_steps: 100
  max_steps: 10000
  eval_every: 500
  save_every: 1000
```

### Class 3 + CP + LoRA (≥ 1B target tokens)
```yaml
stage_1_continued_pretraining:
  base_model: meta-llama/Meta-Llama-3-8B  # post-vocab-extension
  steps: 50000
  learning_rate: 5e-5
  data_mix: {target: 0.80, source: 0.20}
stage_2_lora_task:
  base: <stage 1 output>
  task_data: <bitext / instruction tuning>
  r: 16
  alpha: 32
  steps: 5000
```

### Class 0-1 + HyperOfa + LoRA (no CP — overfits)
```yaml
base_model: facebook/nllb-200-3.3B
vocab_extension: HyperOfa  # initialize new tokens via hypernetwork
lora:
  r: 64
  alpha: 128
  target_modules: all-linear
  modules_to_save: [embed_tokens]
training:
  data_mix: {target: 0.85, source: 0.15}
  learning_rate: 1e-4
  max_steps: 5000  # don't overfit
```

## Eval cadence during training

- Every 500-1000 steps: target-language LM perplexity + source-language LM perplexity (forgetting check) + task metric (chrF, COMET).
- Every 5000 steps: full benchmark eval (FLORES, MasakhaNER, etc.).
- Every checkpoint: save base + adapter; tag with metrics in checkpoint metadata.

## See also

- **Hu, E., et al.** (2021). LoRA paper.
- **Dettmers, T., et al.** (2023). QLoRA.
- **Liu, S.-Y., et al.** (2024). DoRA.
- Unsloth docs: https://docs.unsloth.ai/
- LLaMA-Factory: https://github.com/hiyouga/LLaMA-Factory
- Axolotl: https://github.com/OpenAccess-AI-Collective/axolotl
