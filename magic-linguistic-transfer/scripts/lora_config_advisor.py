"""Recommend LoRA / QLoRA / DoRA config given target language + URIEL distance + base model.

Phase 1 cached recommendations; --measure (live training validation) deferred.
"""

from __future__ import annotations

import argparse
import json
import sys


def lora_for_distance(uriel: float) -> dict:
    if uriel < 0.2:
        return {
            "r": 8,
            "alpha": 16,
            "dropout": 0.05,
            "target_modules": ["q_proj", "v_proj"],
            "rationale": "Close pair: attention-only LoRA sufficient",
            "modules_to_save": [],
        }
    if uriel < 0.4:
        return {
            "r": 16,
            "alpha": 32,
            "dropout": 0.05,
            "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
            "rationale": "Close-moderate: attention all-projections",
            "modules_to_save": [],
        }
    if uriel < 0.6:
        return {
            "r": 32,
            "alpha": 64,
            "dropout": 0.05,
            "target_modules": "all-linear",
            "rationale": "Moderate distance: all-linear LoRA needed",
            "modules_to_save": [],
        }
    if uriel < 0.8:
        return {
            "r": 64,
            "alpha": 128,
            "dropout": 0.05,
            "target_modules": "all-linear",
            "rationale": "Distant: high rank + all-linear; save embed if vocab extended",
            "modules_to_save": ["embed_tokens"],
        }
    return {
        "r": 128,
        "alpha": 256,
        "dropout": 0.05,
        "target_modules": "all-linear",
        "rationale": "Very distant: highest practical rank; consider full fine-tune as alternative",
        "modules_to_save": ["embed_tokens", "lm_head"],
    }


def tool_recommendation(setup: str) -> dict:
    s = setup.lower()
    if "single-gpu" in s or "single_gpu" in s or s == "single":
        return {
            "primary": "Unsloth",
            "rationale": "2× faster than LLaMA-Factory on single GPU; great QLoRA defaults",
            "fallback": "Axolotl (YAML config) or LLaMA-Factory",
        }
    if "multi-gpu" in s or "multi_gpu" in s or "multilingual" in s:
        return {
            "primary": "LLaMA-Factory",
            "rationale": "Multi-GPU + complex multilingual sampling weights",
            "fallback": "Axolotl",
        }
    if "yaml" in s:
        return {
            "primary": "Axolotl",
            "rationale": "Ergonomic YAML config; reproducible",
            "fallback": "LLaMA-Factory",
        }
    if "adapter" in s or "mad-x" in s or "bad-x" in s:
        return {
            "primary": "HuggingFace adapters library",
            "rationale": "MAD-X / BAD-X / Pfeiffer stacking native support",
            "fallback": "PEFT directly",
        }
    return {
        "primary": "Unsloth (recommended default for new projects)",
        "rationale": "Fastest QLoRA; sensible defaults; growing model coverage",
        "fallback": "LLaMA-Factory if multi-GPU; Axolotl for YAML",
    }


def forgetting_mitigation(commercial: bool) -> dict:
    if commercial:
        return {
            "source_data_mix_pct": 20,
            "regularization": "Fisher-weighted (EWC)",
            "lambda_ewc": 0.05,
            "monitor_source_eval_every_steps": 500,
            "rationale": "Commercial deployment: source-language quality affects users; strongest mitigation",
        }
    return {
        "source_data_mix_pct": 15,
        "regularization": "KL to base (lighter than EWC)",
        "kl_beta": 0.05,
        "monitor_source_eval_every_steps": 1000,
        "rationale": "Standard mitigation; lighter than EWC; usually sufficient",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="LoRA config advisor.")
    parser.add_argument(
        "--uriel", type=float, required=True, help="URIEL distance to chosen source language (from magic-linguistic-scope)"
    )
    parser.add_argument("--base-model", default="unspecified", help="Base model name (informational)")
    parser.add_argument("--setup", default="single-gpu", help="single-gpu | multi-gpu | yaml | adapter")
    parser.add_argument(
        "--commercial", action="store_true", help="Commercial deployment (stronger forgetting mitigation)"
    )
    parser.add_argument(
        "--vocab-extended", action="store_true", help="Vocab has been extended (impacts embed_tokens save)"
    )
    args = parser.parse_args()

    if not (0.0 <= args.uriel <= 1.0):
        print("ERROR: --uriel must be in [0.0, 1.0]", file=sys.stderr)
        return 1

    lora = lora_for_distance(args.uriel)
    if not args.vocab_extended:
        # Don't save embed_tokens if vocab not extended
        lora["modules_to_save"] = [m for m in lora["modules_to_save"] if m not in ("embed_tokens", "lm_head")]

    out = {
        "snapshot_date": "2026-04-23",
        "input": {
            "uriel_distance": args.uriel,
            "base_model": args.base_model,
            "setup": args.setup,
            "commercial": args.commercial,
            "vocab_extended": args.vocab_extended,
        },
        "lora_config": lora,
        "tool_recommendation": tool_recommendation(args.setup),
        "forgetting_mitigation": forgetting_mitigation(args.commercial),
        "training_defaults": {
            "learning_rate": 1e-4,
            "warmup_steps": 100,
            "batch_size_effective": 32,
            "max_steps_initial": 5000,
            "eval_every_steps": 500,
            "save_every_steps": 1000,
        },
        "anti_patterns_to_avoid": [
            "DO NOT use LoRA r<8 for URIEL>0.4",
            "DO NOT use attention-only LoRA for URIEL>0.4",
            "DO NOT skip source-language data mix (catastrophic forgetting)",
            "DO NOT continued-pretrain with < 100M target tokens",
        ],
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
