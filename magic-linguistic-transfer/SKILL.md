---
name: magic-linguistic-transfer
description: 'Plan cross-lingual adaptation of pretrained LLMs: LoRA / QLoRA / DoRA config (rank scales with typological distance, not data size), MAD-X / BAD-X adapter stacks, source-language selection via URIEL, continued-pretraining-vs-LoRA decision, catastrophic-forgetting mitigation, tool selection (Unsloth vs LLaMA-Factory vs Axolotl). Use whenever the user mentions LoRA, QLoRA, DoRA, adapter, MAD-X, BAD-X, vocab extension transfer, continued pretraining, fine-tuning a multilingual model for [language], catastrophic forgetting, Unsloth, LLaMA-Factory, Axolotl, PEFT, or asks ''how do I add [language] support to [model]''. **Use BEFORE running training jobs** — wrong adapter choice or rank wastes weeks of compute. Routed by magic-linguistic-orchestrator in the Adapt phase (now part of Acquire+Analyze).'
license: Apache-2.0
compatibility: Python 3.12+
metadata:
  domain: linguistics
  complexity: high
  requires_llm: false
  phase: 2
  supports_pipeline: true
  supports_generation: false
  entry_point: false
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - linguistics
  - transfer-learning
  - lora
  - peft
  - adapter
  - multilingual
  - low-resource
  dependencies: []
  scripts:
  - scripts/lora_config_advisor.py
  - scripts/uriel_transfer_plan.py
---

## When to Use

- Adding a new language to an existing pretrained LLM (Llama-3, Mistral, Qwen, mBART, NLLB, BLOOM, etc.).
- Choosing LoRA rank, alpha, target modules.
- Choosing between continued pretraining vs LoRA vs full fine-tune.
- Picking a tool (Unsloth, LLaMA-Factory, Axolotl, adapters library, PEFT).
- Designing catastrophic-forgetting mitigation.
- Picking adapter stack (MAD-X language + task adapters).

**When NOT to use:** training English-only with abundant data → standard fine-tune; no transfer-learning specialist needed. Pure tokenizer audit → `magic-linguistic-tokenize`. Source language selection without adapter context → `magic-linguistic-scope`.

## The Knowledge Engineers Routinely Miss

1. **LoRA rank scales with typological distance, not data size.** This is the single most common error. r=8 is fine for English-Spanish; r=64+ for English-Inuktitut. URIEL distance is the right input — `magic-linguistic-scope` provides it.

2. **Continued pretraining requires ≥ 1B target tokens AND budget.** Below 100M target tokens, CP overfits + forgets source. LoRA + vocab extension is the sane path for class 1-3.

3. **Unsloth is 2× faster than LLaMA-Factory** for single-GPU QLoRA. LLaMA-Factory wins on multi-GPU + complex multilingual sampling. Axolotl is the YAML-config middle ground. Pick based on setup, not popularity.

4. **Catastrophic forgetting mitigation requires source-language data in the mix.** 10-20% source-lang in training prevents most forgetting. Fisher-weighted regularization > plain L2. Pure-target-language LoRA forgets source.

5. **Adapter stacking (MAD-X) helps when you need multilingual + multi-task.** Single-language + single-task: just use LoRA. Don't over-engineer.

6. **Vocab-extension method must align with transfer choice.** FOCUS pairs with continued pretraining; OFA pairs with LoRA; HyperOfa pairs with LoRA. Mismatches (e.g., HyperOfa + full-fine-tune-without-LoRA) waste the hyper-network init.

7. **LoRA on attention-only vs all-linear matters.** Attention-only (q_proj, v_proj) is the legacy default; current best practice is all-linear (q, k, v, o, gate, up, down) for typologically-distant transfer. Attention-only loses 2-5 BLEU points on hard pairs.

## Workflow

### Step 1 — Pull scope-phase outputs
Read `workspace_state.md`. Confirm: target language(s), Joshi class(es), URIEL distance to candidate sources, vocab-extension plan from `magic-linguistic-tokenize`.

### Step 2 — Decide overall approach

**MANDATORY READ** [`references/adapter_patterns.md`](references/adapter_patterns.md).

| Target class | Parallel data | Best source URIEL | Recommended approach |
|---|---|---|---|
| 0-1 | < 10K | any | Vocab extension (HyperOfa) + LoRA + multilingual base |
| 1-2 | 10K-100K | < 0.4 | OFA vocab extension + LoRA r=16-32 |
| 1-2 | 10K-100K | 0.4-0.6 | OFA + LoRA r=32-64 |
| 1-2 | 10K-100K | > 0.6 | Multilingual base + HyperOfa + LoRA r=32+ |
| 2-3 | 100K-1M | < 0.4 | Continued pretraining + LoRA |
| 2-3 | 100K-1M | > 0.6 | Vocab extension + LoRA r=32-64 (NOT CP — typology too far) |
| 3-4 | 1M-10M | any | Continued pretraining + LoRA OR full fine-tune |
| 5 | abundant | any | Standard full fine-tune |

### Step 3 — LoRA config

**MANDATORY READ** [`references/finetuning_recipes.md`](references/finetuning_recipes.md).

Use `scripts/lora_config_advisor.py`:

| URIEL distance | Recommended rank | Alpha | Target modules |
|---|---|---|---|
| < 0.2 (close pair) | 8 | 16 | attention only acceptable |
| 0.2 - 0.4 | 16 | 32 | all-linear recommended |
| 0.4 - 0.6 | 32 | 64 | all-linear |
| 0.6 - 0.8 | 64 | 128 | all-linear + embed_tokens (if vocab extended) |
| > 0.8 | 128+ | 256 | all-linear + embed_tokens; consider full fine-tune |

### Step 4 — Catastrophic-forgetting mitigation

**MANDATORY READ** [`references/forgetting_mitigation.md`](references/forgetting_mitigation.md).

| Mitigation | When |
|---|---|
| Mix 10-20% source-language data in training | ALWAYS for cross-lingual fine-tune |
| Fisher-weighted regularization (EWC) | When source quality must be preserved (e.g., commercial product where English degradation = customer complaint) |
| KL regularization to base model | Lighter alternative to EWC; less compute |
| Source-task eval throughout training | ALWAYS — catch forgetting early, not post-hoc |

### Step 5 — Source language selection

**MANDATORY READ** [`references/source_selection.md`](references/source_selection.md).

Route to `magic-linguistic-scope` `uriel_distance.py` for top-3 typologically-close + data-available candidates. Use `scripts/uriel_transfer_plan.py` to consolidate.

### Step 6 — Tool selection

| Setup | Recommend |
|---|---|
| Single GPU + QLoRA + speed-priority | Unsloth |
| Multi-GPU + complex multilingual sampling | LLaMA-Factory |
| YAML-config + ergonomics | Axolotl |
| MAD-X / BAD-X adapter stacking | adapters library (HuggingFace) |
| Just want a baseline | PEFT directly |

### Step 7 — Output transfer plan + hand off

Write to `workspace_state.md` under "Transfer Plan". Hand off to `magic-linguistic-eval` for benchmark choice.

## Anti-patterns (NEVER do)

- **NEVER** use LoRA r=4 for typologically-distant pairs. The model can't represent the needed adaptation; you waste compute.
- **NEVER** ignore URIEL distance when picking source language. English is rarely the optimal source.
- **NEVER** continued-pretrain with < 100M target tokens. Over-fits + forgets source.
- **NEVER** skip the source-language data mix (10-20%) for cross-lingual fine-tune. Catastrophic forgetting is preventable; don't let it happen.
- **NEVER** use attention-only LoRA target modules for typologically-distant transfer. Use all-linear.
- **NEVER** assume tool choice doesn't matter. Unsloth-vs-LLaMA-Factory-vs-Axolotl differs in 2x speed + complex-sampling support.
- **NEVER** mix vocab-extension methods with incompatible transfer (HyperOfa + full fine-tune without LoRA wastes the hyper-network init).
- **NEVER** report adapter results without source-task eval baseline (forgetting is invisible without it).

## Edge Cases

- **Multilingual target (5+ languages at once)**: use sampling-weight tuning (α=0.3-0.5 over per-language data); LLaMA-Factory > Unsloth for this.
- **Limited GPU memory + large model (70B Llama-3)**: QLoRA 4-bit; rank lower (16-32 max); accept slower convergence.
- **Target shares vocab heavily with source (Mandarin Han for Cantonese)**: vocab extension may be unnecessary; check overlap first.
- **No usable parallel data + Class 0-1**: HyperOfa + LoRA on multilingual base is the floor; expect modest results; document as Class-0 prototype.
- **Commercial deployment + English degradation unacceptable**: EWC + 20% English data + monitor English perplexity per epoch.
- **Domain shift on top of language shift** (general English → medical Yoruba): two-stage LoRA — first language adapt, then domain adapt; or DoRA which handles multi-direction better.

## Output Format

```markdown
## Transfer Plan: <Target Language>

**Base model:** ... (with rationale: multilingual / English / closely-related)
**Approach:** Continued pretraining | OFA + LoRA | HyperOfa + LoRA | Full fine-tune
**LoRA config:**
  - rank: <N> (rationale: URIEL distance <X>)
  - alpha: <2N>
  - target modules: <attention-only | all-linear | all-linear+embed>
  - dropout: 0.05
**Forgetting mitigation:**
  - Source-language data mix: <X%>
  - Regularization: <EWC | KL | none>
  - Source-task eval cadence: every <N> steps
**Tool:** Unsloth | LLaMA-Factory | Axolotl | adapters | PEFT
**Estimated training tokens:** ~N
**Estimated GPU-hours:** ~N
**Hand-off:** magic-linguistic-eval for benchmark + metric selection
```
