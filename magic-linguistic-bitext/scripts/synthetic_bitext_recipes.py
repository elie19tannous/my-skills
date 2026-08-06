"""Recommend synthetic-bitext strategy when real parallel data is insufficient.

Phase 1: returns recommended strategy + config based on real-pair count + target class.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

def _linguistic_shared_dir() -> str:
    for _p in Path(__file__).resolve().parents:
        _c = _p / "_linguistic_shared"
        if _c.is_dir():
            return str(_c)
    raise RuntimeError("_linguistic_shared bundle not found — run scripts/sync-linguistic-shared.py")
sys.path.insert(0, _linguistic_shared_dir())
from lang_codes import resolve_language  # noqa: E402


def recommend(real_pairs: int, target_class: int | None, has_dictionary: bool, has_pivot_pair: bool) -> dict:
    # `out` accumulates heterogeneous values (lists, str, dict). Widen to Any for mypy.
    out: dict[str, Any] = {"strategies": [], "warnings": []}

    if real_pairs >= 1_000_000:
        out["overall"] = "Synthetic bitext NOT needed; real parallel sufficient."
        return out
    if real_pairs >= 100_000:
        out["overall"] = "Synthetic bitext OPTIONAL; consider for domain coverage gaps."
    elif real_pairs >= 10_000:
        out["overall"] = "Synthetic bitext RECOMMENDED."
    else:
        out["overall"] = "Synthetic bitext ESSENTIAL. Quality limitations expected."

    # Back-translation recommendation
    if real_pairs >= 5_000:
        out["strategies"].append(
            {
                "method": "back_translation",
                "config": {
                    "temperature": 0.9,
                    "top_p": 0.95,
                    "tag_synthetic_with": "<bt>",
                    "synthetic_to_real_ratio_target": "3-5×",
                },
                "rationale": "Sufficient real pairs to train target→source baseline; back-translate target monolingual.",  # noqa: E501  # long anti-pattern string
            }
        )
    else:
        out["warnings"].append("Real pairs < 5000 → back-translation baseline will be weak; expect noisier synthetic.")

    # Dictionary substitution
    if has_dictionary:
        out["strategies"].append(
            {
                "method": "dictionary_substitution",
                "config": {
                    "lexicon_size_min": 10_000,
                    "code_switch_ratio": "30-50%",
                },
                "rationale": "Lexicon available — code-switched augmentation builds cross-lingual signal cheaply.",
            }
        )
    else:
        out["warnings"].append(
            "No dictionary available → consider extracting one (Wiktionary, panlex, MUSE bilingual lexicons)."
        )

    # Pivot
    if has_pivot_pair:
        out["strategies"].append(
            {
                "method": "pivot_mt",
                "config": {
                    "intermediate_choice": "user-specified (high-quality intermediate pair)",
                    "expected_quality_loss": "~0.10 BLEU per pivot hop",
                },
                "rationale": "Pivot MT can beat direct when intermediate pair is dramatically better-resourced.",
            }
        )

    # Quality control
    out["quality_control"] = {
        "round_trip_check": "Forward-MT a sample back to source; round-trip BLEU ≥ 30 = OK",
        "length_ratio_filter": "Apply same as real bitext (see alignment_score.py)",
        "native_speaker_spot_check": "100 samples; precision ≥ 90%",
        "synthetic_real_ratio_max": "5× before model learns synthetic noise",
    }

    out["anti_patterns"] = [
        "DO NOT back-translate with T=0 (translationese drift)",
        "DO NOT mix synthetic + real WITHOUT a `<bt>` or `<synthetic>` tag",
        "DO NOT use the same model's forward output as its own training data (model collapse)",
        "DO NOT pivot through a near-target language without quality-checking the intermediate pair",
    ]
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend synthetic-bitext strategy.")
    parser.add_argument("target", help="Target language")
    parser.add_argument("--real-pairs", type=int, required=True, help="Real parallel pair count for the language pair")
    parser.add_argument("--target-class", type=int, default=None, help="Joshi class of target")
    parser.add_argument("--has-dictionary", action="store_true", help="Bilingual lexicon available")
    parser.add_argument("--has-pivot-pair", action="store_true", help="High-quality intermediate pair available")
    args = parser.parse_args()

    try:
        tgt = resolve_language(args.target)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    rec = recommend(args.real_pairs, args.target_class, args.has_dictionary, args.has_pivot_pair)
    out = {
        "target": tgt.display,
        "iso639_3": tgt.iso639_3,
        "real_pairs_input": args.real_pairs,
        **rec,
        "snapshot_date": "2026-04-23",
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
