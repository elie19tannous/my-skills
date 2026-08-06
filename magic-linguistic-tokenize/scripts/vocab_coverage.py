"""Estimate character coverage required for a script + recommend SentencePiece config.

Phase 1: returns recommendations from cached per-script tables.
Phase 2+: --measure to compute coverage on a real corpus.
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

# Per-script recommended SentencePiece config (snapshot 2026-04-23).
_SCRIPT_RECS: dict[str, dict] = {
    "Latin": {
        "character_coverage": 0.9999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 64000,
        "add_dummy_prefix": True,
        "rationale": "Limited inventory; rare chars often OCR errors. byte_fallback for safety.",
    },
    "Cyrillic": {
        "character_coverage": 0.9999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 64000,
        "add_dummy_prefix": True,
        "rationale": "Same rationale as Latin.",
    },
    "Greek": {
        "character_coverage": 0.9999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 50000,
        "add_dummy_prefix": True,
        "rationale": "Modern + polytonic; coverage 0.9999 OK with byte_fallback.",
    },
    "Devanagari": {
        "character_coverage": 0.99999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 80000,
        "add_dummy_prefix": True,
        "rationale": "Conjuncts and variants are semantically meaningful. High coverage required.",
    },
    "Bengali": {
        "character_coverage": 0.99999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 80000,
        "add_dummy_prefix": True,
        "rationale": "Indic conjuncts; high coverage required.",
    },
    "Tamil": {
        "character_coverage": 0.99999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 80000,
        "add_dummy_prefix": True,
        "rationale": "Indic conjuncts; high coverage required.",
    },
    "Han": {
        "character_coverage": 0.99999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 100000,
        "add_dummy_prefix": False,
        "rationale": "5000+ rare characters (names, archaic forms) carry meaning. Coverage 0.99999 critical. Han is space-less so add_dummy_prefix=false.",  # noqa: E501  # long anti-pattern string
    },
    "Hangul": {
        "character_coverage": 0.99999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 64000,
        "add_dummy_prefix": True,
        "rationale": "Composable jamo; high coverage required.",
    },
    "Han+Kana": {
        "character_coverage": 0.99999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 100000,
        "add_dummy_prefix": False,
        "rationale": "Japanese: Han + Hiragana + Katakana + Latin code-mix. High coverage; space-less.",
    },
    "Arabic": {
        "character_coverage": 0.99999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 64000,
        "add_dummy_prefix": True,
        "rationale": "Letter forms + presentation forms + diacritics. Do NOT NFKC-normalize upstream; tokenizer expects forms preserved.",  # noqa: E501  # long anti-pattern string
    },
    "Hebrew": {
        "character_coverage": 0.99999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 50000,
        "add_dummy_prefix": True,
        "rationale": "Niqqud + final-form letters; high coverage required.",
    },
    "Khmer": {
        "character_coverage": 0.99999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 50000,
        "add_dummy_prefix": False,
        "rationale": "Complex sub-script diacritics; space-less words. Word segmentation required upstream.",
    },
    "Myanmar": {
        "character_coverage": 0.99999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 50000,
        "add_dummy_prefix": False,
        "rationale": "Stacked consonants; word segmentation required upstream.",
    },
    "Thai": {
        "character_coverage": 0.99999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 50000,
        "add_dummy_prefix": False,
        "rationale": "Space-less; word segmentation required upstream (e.g., PyThaiNLP).",
    },
    "Tibetan": {
        "character_coverage": 0.99999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 30000,
        "add_dummy_prefix": False,
        "rationale": "Stacked consonants; segmentation by syllable mark.",
    },
    "Ge'ez": {
        "character_coverage": 0.99999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 50000,
        "add_dummy_prefix": True,
        "rationale": "Amharic / Tigrinya. Syllabary; high coverage.",
    },
    "Cherokee": {
        "character_coverage": 0.99999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 16000,
        "add_dummy_prefix": True,
        "rationale": "Syllabary; class 0-1 — small vocab, byte_fallback critical.",
    },
    "Canadian Aboriginal Syllabics": {
        "character_coverage": 0.99999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 16000,
        "add_dummy_prefix": False,
        "rationale": "Inuktitut/Cree; class 0-1; small vocab + byte_fallback.",
    },
    "Georgian": {
        "character_coverage": 0.9999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 32000,
        "add_dummy_prefix": True,
        "rationale": "Limited inventory; standard Latin-like config.",
    },
    "Lao": {
        "character_coverage": 0.99999,
        "byte_fallback": True,
        "model_type": "unigram",
        "vocab_size_hint": 32000,
        "add_dummy_prefix": False,
        "rationale": "Space-less; segmentation required upstream.",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend SentencePiece config for a language's script.")
    parser.add_argument("language", help="Language name or ISO 639-3 code")
    parser.add_argument("--measure", action="store_true", help="(Phase 2+) measure coverage on a real corpus")
    args = parser.parse_args()

    if args.measure:
        print("ERROR: --measure is Phase 2+. Cached recommendations only in Phase 1.", file=sys.stderr)
        return 2

    try:
        rec = resolve_language(args.language)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    primary_script = rec.script_default.split("+")[0] if rec.script_default else "Unknown"
    config = _SCRIPT_RECS.get(primary_script)
    if config is None:
        print(
            json.dumps(
                {
                    "language": rec.display,
                    "iso639_3": rec.iso639_3,
                    "script": primary_script,
                    "warning": f"No cached config for script {primary_script!r}. Use Tool-pattern defaults: unigram, char_cov 0.9999, byte_fallback=true.",  # noqa: E501  # long anti-pattern string
                },
                indent=2,
            )
        )
        return 4

    out = {
        "language": rec.display,
        "iso639_3": rec.iso639_3,
        "primary_script": primary_script,
        "secondary_scripts": rec.script_default.split("+")[1:] if "+" in rec.script_default else [],
        "recommended_sentencepiece_config": {
            "model_type": config["model_type"],
            "vocab_size_hint": config["vocab_size_hint"],
            "character_coverage": config["character_coverage"],
            "byte_fallback": config["byte_fallback"],
            "add_dummy_prefix": config["add_dummy_prefix"],
            "split_digits": True,
            "normalization_rule_name": "identity",
        },
        "rationale": config["rationale"],
        "snapshot_date": "2026-04-23",
    }
    if rec.notes:
        out["language_notes"] = rec.notes
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
