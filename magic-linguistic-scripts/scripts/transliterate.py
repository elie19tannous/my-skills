"""Transliterate / romanize text using cached scheme tables.

Recommends the right scheme per script and performs lightweight transliteration
for common cases. For production-grade Indic transliteration, prefer Aksharamukha;
for cross-script work, prefer ICU.

Phase 1 ships a small cached table; --use-aksharamukha and --use-icu paths are
Phase 2+ stubs.
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

# Recommended scheme per script (cached). reversibility: True/False/Approx.
_SCHEMES: dict[str, dict] = {
    "Devanagari": {"scheme": "IAST", "reversible": True, "tool": "aksharamukha"},
    "Bengali": {"scheme": "IAST", "reversible": True, "tool": "aksharamukha"},
    "Tamil": {"scheme": "ISO 15919", "reversible": True, "tool": "aksharamukha"},
    "Telugu": {"scheme": "ISO 15919", "reversible": True, "tool": "aksharamukha"},
    "Kannada": {"scheme": "ISO 15919", "reversible": True, "tool": "aksharamukha"},
    "Malayalam": {"scheme": "ISO 15919", "reversible": True, "tool": "aksharamukha"},
    "Gujarati": {"scheme": "ISO 15919", "reversible": True, "tool": "aksharamukha"},
    "Gurmukhi": {"scheme": "ISO 15919", "reversible": True, "tool": "aksharamukha"},
    "Greek": {"scheme": "ISO 843", "reversible": True, "tool": "icu"},
    "Cyrillic": {"scheme": "ISO 9", "reversible": True, "tool": "icu"},
    "Arabic": {"scheme": "ALA-LC (or Buckwalter for NLP)", "reversible": "Approx", "tool": "custom"},
    "Hebrew": {"scheme": "ISO 259", "reversible": "Approx", "tool": "custom"},
    "Han": {"scheme": "Pinyin (Mandarin) / Jyutping (Cantonese)", "reversible": False, "tool": "pinyin/jyutping"},
    "Hangul": {"scheme": "Revised Romanization (2000)", "reversible": True, "tool": "icu"},
    "Hiragana": {"scheme": "Hepburn", "reversible": True, "tool": "pykakasi"},
    "Katakana": {"scheme": "Hepburn", "reversible": True, "tool": "pykakasi"},
    "Thai": {"scheme": "RTGS (lossy) or ISO 11940", "reversible": False, "tool": "custom"},
    "Khmer": {"scheme": "UN System", "reversible": "Approx", "tool": "custom"},
    "Myanmar": {"scheme": "MLC Transcription", "reversible": "Approx", "tool": "custom"},
    "Tibetan": {"scheme": "Wylie", "reversible": True, "tool": "custom"},
    "Cherokee": {"scheme": "Latin (community-defined)", "reversible": "Approx", "tool": "custom"},
    "Canadian Aboriginal Syllabics": {"scheme": "Latin (community-defined)", "reversible": "Approx", "tool": "custom"},
    "Ge'ez": {"scheme": "BGN/PCGN (Ge'ez)", "reversible": True, "tool": "custom"},
    "Latin": {"scheme": "(already Latin)", "reversible": True, "tool": "n/a"},
}


def recommend_for_language(query: str) -> dict:
    rec = resolve_language(query)
    script = rec.script_default.split("+")[0]  # take primary if multi-script
    if script in _SCHEMES:
        scheme_info = _SCHEMES[script]
    else:
        scheme_info = {"scheme": "UNKNOWN", "reversible": None, "tool": "research-needed"}
    return {
        "language": rec.display,
        "iso639_3": rec.iso639_3,
        "script": script,
        **scheme_info,
        "snapshot_date": "2026-04-23",
        "notes": rec.notes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend romanization scheme for a language.")
    parser.add_argument("language", help="Language name or ISO 639-3 code")
    parser.add_argument(
        "--use-aksharamukha", action="store_true", help="(Phase 2+) actually transliterate via Aksharamukha"
    )
    parser.add_argument("--use-icu", action="store_true", help="(Phase 2+) actually transliterate via ICU")
    args = parser.parse_args()

    if args.use_aksharamukha or args.use_icu:
        print(
            "ERROR: actual transliteration via aksharamukha/ICU is Phase 2+. "
            "Phase 1 returns scheme recommendations only.",
            file=sys.stderr,
        )
        return 2

    try:
        info = recommend_for_language(args.language)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(json.dumps(info, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
