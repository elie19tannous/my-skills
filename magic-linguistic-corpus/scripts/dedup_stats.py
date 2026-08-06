"""Recommend MinHash dedup config for a corpus + analyze given dedup-stats input.

Phase 1 cached: per-(language-class, script) recommended config.
Phase 2+: --measure to actually compute MinHash on input corpus.
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


def recommend_config(iso: str, joshi_class: int | None, script: str) -> dict:
    # Threshold by resource class
    if joshi_class is not None and joshi_class <= 2:
        threshold = 0.9
        threshold_rationale = "Class 0-2: short-content over-merging risk; 0.9 retains valid distinct entries"
    elif joshi_class is not None and joshi_class >= 4:
        threshold = 0.85
        threshold_rationale = "Class 4-5: large corpus, standard 0.85 OK"
    else:
        threshold = 0.85
        threshold_rationale = "Class 3 (or unknown): standard 0.85"

    # Shingle size by script
    if script in ("Han", "Han+Kana", "Khmer", "Myanmar", "Thai", "Tibetan", "Lao"):
        shingle_size = 3
        shingle_rationale = f"Space-less script ({script}): smaller char shingles capture meaningful units"
    elif script in (
        "Devanagari",
        "Bengali",
        "Tamil",
        "Telugu",
        "Kannada",
        "Malayalam",
        "Gujarati",
        "Gurmukhi",
        "Arabic",
        "Hebrew",
    ):
        shingle_size = 4
        shingle_rationale = f"Indic / abjad ({script}): mid-length char shingles for conjunct handling"
    else:
        shingle_size = 5
        shingle_rationale = f"Latin/Cyrillic-like ({script}): standard 5-char shingles"

    return {
        "num_perm": 256,
        "threshold": threshold,
        "threshold_rationale": threshold_rationale,
        "shingle_size": shingle_size,
        "shingle_rationale": shingle_rationale,
        "shingle_type": "character",
        "pre_dedup_steps_required": [
            "1. Unicode NFC normalization (route to magic-linguistic-scripts)",
            "2. TR39 confusable folding for dedup KEY only (route to magic-linguistic-scripts)",
            "3. Lower-case + whitespace collapse for key",
            "4. BOM + ZWJ/ZWNJ removal from key",
        ],
        "warning": "ALWAYS run cross-dataset dedup AFTER concatenation, not within each dataset",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend MinHash dedup config + analyze dedup output.")
    parser.add_argument("language", help="Language name or ISO 639-3 code")
    parser.add_argument("--joshi-class", type=int, default=None, help="Joshi 0-5 class (from magic-linguistic-scope)")
    parser.add_argument("--measure", help="(Phase 2+) compute MinHash on input file")
    args = parser.parse_args()

    if args.measure:
        print(
            "ERROR: --measure (live MinHash compute) deferred to Phase 2+. Recommend config only in Phase 1.",
            file=sys.stderr,
        )
        return 2

    try:
        rec = resolve_language(args.language)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    primary_script = rec.script_default.split("+")[0] if rec.script_default else "Unknown"
    config = recommend_config(rec.iso639_3, args.joshi_class, primary_script)

    out = {
        "language": rec.display,
        "iso639_3": rec.iso639_3,
        "primary_script": primary_script,
        "joshi_class_input": args.joshi_class,
        "recommended_minhash_config": config,
        "snapshot_date": "2026-04-23",
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
