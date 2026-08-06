# Catastrophic Forgetting Mitigation — Reference

Loaded by `magic-linguistic-transfer` Step 4.

## What forgetting is

When a pretrained model is fine-tuned on a new distribution (target language), it loses capability on the old distribution (source language) unless explicitly preserved. For cross-lingual fine-tune:

- Pure-target LoRA on Llama-3 with no English mix → English perplexity rises 20-50% in 5K steps.
- 10% English mix → English perplexity stable; target adaptation slightly slower.
- 20% English mix → English perplexity may improve slightly; target slower.

Forgetting matters when:
- Commercial product where source-lang quality affects users.
- Multilingual model where source-lang task is also evaluated.
- Iterative training where you'll need to fine-tune again on source later.

Forgetting is acceptable when:
- Target-only deployment with explicit single-language design.
- One-shot research probe.

## Mitigation techniques (lightest to heaviest)

### 1. Source-language data mix (always do this)

Mix 10-20% source-language data in the training stream. Cheapest, most effective single intervention.

```python
def mixed_dataloader(target_data, source_data, source_ratio=0.15):
    while True:
        if random() < source_ratio:
            yield next(source_data)
        else:
            yield next(target_data)
```

### 2. KL-divergence regularization to base model

Penalize divergence from base model's outputs (only on layers being trained). Lighter than EWC.

```python
loss = ce_loss + beta * kl_div(model_logits, base_model_logits)
# beta typically 0.01-0.1
```

### 3. Elastic Weight Consolidation (EWC) / Fisher-weighted regularization

Penalize changes to parameters that mattered for source-language performance. Compute Fisher information on a source sample BEFORE fine-tuning; use as weight on L2 regularization during target fine-tune.

```python
# Pre-compute Fisher diagonal on source data
fisher = compute_fisher(model, source_eval_data)
# Apply during fine-tune
loss = ce_loss + lambda_ewc * sum(f * (theta - theta_base)**2 for f, theta, theta_base in zip(fisher, current_params, base_params))
```

EWC is heavier (need source data + Fisher computation) but the strongest regularization for protecting specific capabilities.

### 4. Adapter approach (architectural)

LoRA / adapters by design freeze most of the base model. Forgetting is minimized at the architecture level. Combined with source-mix, this is usually sufficient.

### 5. Replay buffer

Keep a buffer of representative source examples; periodically train on them. More compute-heavy version of source-mix.

### 6. Modular models (separate language adapters)

MAD-X-style: source-lang adapter + target-lang adapter; switch at inference. No forgetting because base + per-lang adapters never interact during forward pass. More complex deployment.

## Monitoring during training

ALWAYS evaluate source-language perplexity / task metric every 500-1000 steps. Catch forgetting early:

| Symptom | Likely cause | Fix |
|---|---|---|
| Source perplexity rising > 5% per 1K steps | Insufficient source-mix | Raise to 20% |
| Source perplexity stable, target plateauing | Over-regularized | Reduce KL beta or EWC lambda |
| Target loss dropping but eval flat | Overfitting on training distribution | Add more diverse target data; lower LR |
| Both source and target perplexity rising | Bug — wrong base model? Wrong tokenizer? | Diagnose first |

## When NOT to mitigate

- **Single-language deployment**, source-lang quality irrelevant, no future fine-tunes planned: skip mitigation; full target focus may be optimal.
- **Massive target data + budget**: continued pretraining at scale natively learns source via mix; extra mitigation unnecessary.

## See also

- **Kirkpatrick, J., et al.** (2017). *Overcoming catastrophic forgetting in neural networks* (EWC). PNAS.
- **Aghajanyan, A., et al.** (2021). *Better Fine-Tuning by Reducing Representational Collapse* (R3F). ICLR.
- **Howard, J., & Ruder, S.** (2018). *Universal Language Model Fine-tuning for Text Classification* (ULMFiT). ACL — gradual unfreezing as alternative.
- **Ramasesh, V., et al.** (2022). *Effect of scale on catastrophic forgetting in neural networks*. ICLR — observation that scale alone helps.
