"""Recommend contamination-audit checks for an eval set vs. a training mix.

Phase 1: returns recommended checks + cached known-inclusion proxies.
Phase 2+: --measure to actually compute n-gram overlap.
"""

from __future__ import annotations

import argparse
import json
import sys

# Cached known-inclusion proxies (snapshot 2026-04-23).
# Eval set → known to be in known pretrain mixes.
_KNOWN_INCLUSIONS: dict[str, dict] = {
    "FLORES-200": {
        "release_date": "2022-07",
        "in_pretrain_likely": ["The Pile", "C4", "CulturaX", "MADLAD-400", "RedPajama"],
        "alternatives": ["NTREX-128 (2022-11)", "your custom held-out (post-cutoff)"],
        "notes": "Often included via HuggingFace dataset cards in pretrain mixes",
    },
    "NTREX-128": {
        "release_date": "2022-11",
        "in_pretrain_likely": ["some 2024+ pretrains"],
        "alternatives": ["custom held-out"],
        "notes": "Less commonly contaminated than FLORES",
    },
    "Belebele": {
        "release_date": "2023-08",
        "in_pretrain_likely": ["likely in 2024+ pretrains"],
        "alternatives": ["custom held-out"],
        "notes": "MC reading comprehension; check per-language",
    },
    "AfroBench": {
        "release_date": "2024-12",
        "in_pretrain_likely": ["unlikely in pre-2025 models"],
        "alternatives": [],
        "notes": "Newer; cleaner",
    },
    "SEACrowd v2": {
        "release_date": "2025-06",
        "in_pretrain_likely": ["unlikely in pre-2025 models"],
        "alternatives": [],
        "notes": "Newer; cleaner",
    },
    "MasakhaNER 2.0": {
        "release_date": "2022-09",
        "in_pretrain_likely": ["likely in any African-NLP-aware pretrain"],
        "alternatives": ["MasakhaNER 1.0 train set as held-out"],
        "notes": "Widely cited",
    },
    "IndicXTREME": {
        "release_date": "2023-04",
        "in_pretrain_likely": ["likely in 2024+ Indic-aware pretrains"],
        "alternatives": ["custom held-out"],
        "notes": "Per-task contamination varies",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend contamination-audit checks for an eval set.")
    parser.add_argument("eval_set", help="Eval set name (e.g., 'FLORES-200', 'NTREX-128', 'Belebele', 'AfroBench')")
    parser.add_argument("--base-model-cutoff", help="Base model training cutoff date (YYYY-MM-DD)")
    parser.add_argument("--measure", action="store_true", help="(Phase 2+) compute actual n-gram overlap")
    args = parser.parse_args()

    if args.measure:
        print(
            "ERROR: --measure (live n-gram audit) deferred to Phase 2+. Recommendations only in Phase 1.",
            file=sys.stderr,
        )
        return 2

    eval_info = _KNOWN_INCLUSIONS.get(args.eval_set)
    if eval_info is None:
        print(
            json.dumps(
                {
                    "eval_set": args.eval_set,
                    "warning": f"No cached inclusion data for {args.eval_set!r}. Run side-(a) check (train-mix vs eval) anyway.",  # noqa: E501  # long anti-pattern string
                    "side_a_check": "13-gram exact-match + MinHash-paraphrase on eval ↔ train",
                    "side_b_check": "Unknown — research base-model pretrain composition",
                },
                indent=2,
            )
        )
        return 4

    out = {
        "eval_set": args.eval_set,
        "snapshot_date": "2026-04-23",
        "eval_release_date": eval_info["release_date"],
        "side_a_check": {
            "method": "13-gram exact match (GPT-3 standard) + 7-gram + MinHash paraphrase",
            "thresholds": {"clean": 0.0, "acceptable": "≤ 2%", "flag": "2-10%", "fail": "> 10%"},
            "tools": "Custom or `decontamination` library",
        },
        "side_b_check": {
            "method": "Compare eval release date vs base-model training cutoff + check known inclusions",
            "in_pretrain_likely": eval_info["in_pretrain_likely"],
            "notes": eval_info["notes"],
            "alternatives": eval_info["alternatives"],
        },
    }

    if args.base_model_cutoff:
        out["base_model_cutoff_input"] = args.base_model_cutoff
        if args.base_model_cutoff < eval_info["release_date"]:
            out["side_b_verdict"] = (
                f"CLEAN — base model cutoff ({args.base_model_cutoff}) precedes eval release ({eval_info['release_date']}); "  # noqa: E501  # long anti-pattern string
                "eval cannot have been memorized"
            )
        else:
            out["side_b_verdict"] = (
                f"AT RISK — base model cutoff ({args.base_model_cutoff}) is AFTER eval release ({eval_info['release_date']}); "  # noqa: E501  # long anti-pattern string
                f"eval may have been seen. Consider: {eval_info['alternatives']}"
            )

    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
