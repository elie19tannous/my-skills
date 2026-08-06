"""Compute tokenizer fertility (tokens/word) for a language vs cached English baseline.

Phase 1 ships cached fertility tables for canonical (tokenizer, language) pairs;
--measure mode (compute fertility on a real corpus + tokenizer) is a Phase 2+
stub. Cached snapshot 2026-04-23.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

def _linguistic_shared_dir() -> str:
    for _p in Path(__file__).resolve().parents:
        _c = _p / "_linguistic_shared"
        if _c.is_dir():
            return str(_c)
    raise RuntimeError("_linguistic_shared bundle not found — run scripts/sync-linguistic-shared.py")
sys.path.insert(0, _linguistic_shared_dir())
from lang_codes import resolve_language  # noqa: E402

# Cached fertility baselines (snapshot 2026-04-23).
# Format: tokenizer -> {iso639_3: tokens_per_word}
_BASELINES: dict[str, dict[str, float]] = {
    "tiktoken-cl100k_base": {
        "eng": 1.4,
        "yor": 3.4,
        "khm": 4.2,
        "vie": 2.1,
        "cmn": 1.6,
        "tur": 2.8,
        "iku": 6.1,
        "swa": 2.4,
        "ibo": 3.1,
        "hau": 2.7,
        "amh": 4.5,
        "tam": 3.0,
        "hin": 2.0,
        "ind": 1.8,
        "kin": 3.2,
        "twi": 3.6,
        "que": 3.9,
        "haw": 2.3,
        "fin": 1.9,
        "hun": 1.9,
        "kaz": 2.9,
        "uzb": 2.6,
        "wol": 3.4,
        "nav": 5.8,
        "mri": 2.3,
        "sme": 3.7,
        "fas": 2.0,
        "arb": 1.8,
        "arz": 2.4,
    },
    "llama-3-128k": {
        "eng": 1.3,
        "yor": 2.9,
        "khm": 3.7,
        "vie": 1.9,
        "cmn": 1.4,
        "tur": 2.4,
        "iku": 5.4,
        "swa": 2.1,
        "ibo": 2.7,
        "hau": 2.4,
        "amh": 3.8,
        "tam": 2.6,
        "hin": 1.7,
        "ind": 1.6,
        "kin": 2.8,
        "twi": 3.1,
    },
    "mbart-250k": {
        "eng": 1.2,
        "yor": 2.0,
        "khm": 2.4,
        "vie": 1.5,
        "cmn": 1.3,
        "tur": 1.7,
        "iku": 3.8,
        "swa": 1.6,
        "ibo": 1.9,
        "hau": 1.7,
        "amh": 2.4,
        "tam": 1.7,
        "hin": 1.4,
        "ind": 1.4,
    },
    "nllb-256k": {
        "eng": 1.3,
        "yor": 1.8,
        "khm": 2.0,
        "vie": 1.5,
        "cmn": 1.3,
        "tur": 1.6,
        "iku": 3.2,
        "swa": 1.5,
        "ibo": 1.8,
        "hau": 1.6,
        "amh": 2.1,
        "tam": 1.5,
        "hin": 1.3,
        "ind": 1.3,
        "kin": 1.8,
        "twi": 2.0,
    },
}


def interpret_ratio(ratio: float) -> tuple[str, str]:
    """Return (verdict, action)."""
    if ratio <= 1.5:
        return "OK", "no action"
    if ratio <= 2.0:
        return "MILD", "optional vocab extension; depends on cost sensitivity"
    if ratio <= 3.0:
        return "HIGH", "vocab extension recommended"
    if ratio < 5.0:
        return "SEVERE", "vocab extension MANDATORY"
    return "CATASTROPHIC", "tokenizer is failing for this language; train new or use language-specialized base"


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute tokenizer fertility ratio for a language.")
    parser.add_argument(
        "--tokenizer",
        required=True,
        choices=list(_BASELINES.keys()),
        help="Tokenizer name (cached baselines available)",
    )
    parser.add_argument("--lang", required=True, help="Target language (name or ISO 639-3)")
    parser.add_argument("--baseline-lang", default="eng", help="Baseline language (default: English)")
    parser.add_argument("--measure", action="store_true", help="(Phase 2+) actually tokenize a corpus and measure live")
    args = parser.parse_args()

    if args.measure:
        print("ERROR: --measure is Phase 2+. Cached baselines only in Phase 1.", file=sys.stderr)
        return 2

    try:
        target = resolve_language(args.lang)
        baseline = resolve_language(args.baseline_lang)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    table = _BASELINES[args.tokenizer]
    if target.iso639_3 not in table:
        print(
            json.dumps(
                {
                    "tokenizer": args.tokenizer,
                    "language": target.display,
                    "iso639_3": target.iso639_3,
                    "warning": f"No cached fertility for ({args.tokenizer}, {target.iso639_3}). Use --measure (Phase 2+) for live computation.",  # noqa: E501  # long anti-pattern string
                },
                indent=2,
            )
        )
        return 4
    if baseline.iso639_3 not in table:
        print(f"ERROR: baseline language {baseline.iso639_3} not in cached table for {args.tokenizer}", file=sys.stderr)
        return 1

    tgt_fert = table[target.iso639_3]
    base_fert = table[baseline.iso639_3]
    ratio = tgt_fert / base_fert
    verdict, action = interpret_ratio(ratio)

    print(
        json.dumps(
            {
                "tokenizer": args.tokenizer,
                "language": target.display,
                "iso639_3": target.iso639_3,
                "fertility": tgt_fert,
                "baseline_language": baseline.display,
                "baseline_fertility": base_fert,
                "ratio": round(ratio, 3),
                "verdict": verdict,
                "action": action,
                "snapshot_date": "2026-04-23",
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
