"""Side-(b) contamination check: eval set vs known base-model pretrain.

Phase 1: cached known-inclusion table + base-model-cutoff comparison.
Cross-references magic-linguistic-corpus/scripts/contamination_audit.py (full audit).
"""

from __future__ import annotations

import argparse
import json
import sys

# Cached known eval-set release dates + base-model pretrain cutoffs (snapshot 2026-04-23).
_EVAL_RELEASES = {
    "FLORES-200": "2022-07",
    "FLORES+": "2022-07",
    "NTREX-128": "2022-11",
    "Belebele": "2023-08",
    "AfroBench": "2024-12",
    "SEACrowd v2": "2025-06",
    "MasakhaNER 2.0": "2024-09",
    "IndicXTREME": "2023-04",
    "TyDi-QA": "2020-03",
    "XQuAD": "2019-10",
    "XNLI": "2018-09",
    "Common Voice": "2017-12",
    "AfriSenti": "2023-01",
}

_MODEL_CUTOFFS = {
    "Llama-3-8B": "2024-03",
    "Llama-3-70B": "2024-03",
    "Llama-3.1": "2024-07",
    "Mistral-7B": "2023-09",
    "GPT-4o": "2023-10",
    "GPT-4-turbo": "2023-12",
    "Claude-3-Opus": "2023-08",
    "Claude-3.5-Sonnet": "2024-04",
    "Claude-Sonnet-4-6": "2026-03",
    "Qwen2-72B": "2024-06",
    "Gemini-1.5": "2024-04",
    "NLLB-200": "2022-07",
}

# Known eval-in-pretrain inclusions (cached snapshot).
_KNOWN_INCLUSIONS = {
    "FLORES-200": ["The Pile", "C4", "CulturaX", "MADLAD-400", "RedPajama"],
    "FLORES+": ["likely in 2024+ pretrains"],
    "NTREX-128": ["some 2024+ pretrains"],
    "Belebele": ["likely in 2024+ pretrains"],
    "Common Voice": ["likely in audio-aware multimodal pretrains"],
    "MasakhaNER 2.0": ["likely in African-NLP-aware pretrains"],
    "IndicXTREME": ["likely in 2024+ Indic-aware pretrains"],
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Side-(b) contamination check: eval vs base-model pretrain.")
    parser.add_argument("--eval-set", required=True, help="Eval set name (e.g., FLORES-200, NTREX-128)")
    parser.add_argument("--base-model", help="Base model (e.g., Llama-3-8B); used for cutoff lookup")
    parser.add_argument("--base-model-cutoff", help="Override: explicit YYYY-MM-DD cutoff")
    args = parser.parse_args()

    eval_release = _EVAL_RELEASES.get(args.eval_set)
    if not eval_release:
        print(
            json.dumps(
                {
                    "eval_set": args.eval_set,
                    "warning": f"No cached release date for {args.eval_set!r}; provide --base-model-cutoff explicitly.",
                },
                indent=2,
            )
        )
        return 4

    cutoff = args.base_model_cutoff
    if not cutoff and args.base_model:
        cutoff = _MODEL_CUTOFFS.get(args.base_model)

    out = {
        "eval_set": args.eval_set,
        "eval_release_date": eval_release,
        "snapshot_date": "2026-04-23",
        "cross_reference": "see magic-linguistic-corpus/scripts/contamination_audit.py for full audit",
    }

    if cutoff:
        out["base_model"] = args.base_model or "specified-cutoff"
        out["base_model_cutoff"] = cutoff
        if cutoff < eval_release:
            out["verdict"] = "CLEAN — base model cutoff precedes eval release; eval cannot be memorized"
            out["score_interpretation"] = "Standard: report as direct measurement"
        else:
            out["verdict"] = (
                f"AT RISK — base model cutoff ({cutoff}) is AFTER eval release ({eval_release}); "
                "eval may be in pretrain"
            )
            out["score_interpretation"] = "LOWER BOUND: model has likely seen this eval; report transparently"
            inclusions = _KNOWN_INCLUSIONS.get(args.eval_set, [])
            if inclusions:
                out["known_pretrain_inclusions"] = inclusions
            out["recommendation"] = (
                "Switch to alternative eval (NTREX-128, AfroBench, SEACrowd v2, custom held-out post-cutoff) "
                "for unbiased measurement; OR report contaminated eval as lower bound + flag transparently in model card"  # noqa: E501  # long anti-pattern string
            )
    else:
        out["warning"] = "No base-model cutoff provided; cannot compute side-(b) contamination risk."

    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
