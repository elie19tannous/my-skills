"""Detect TR39-style script confusables (Latin look-alikes from other scripts).

Two modes:
- detect (default): scan and report positions, no transformation.
- fold: produce a confusable-folded version for use as DEDUP KEY ONLY (never store as canonical).

Cached approximation of TR39 (2026-04-23 snapshot). For full TR39 fidelity, install
`confusable_homoglyphs` and pass --use-confusable-homoglyphs.
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from collections import Counter

# Cached approximation of TR39 skeleton (high-frequency confusables).
# Maps non-Latin look-alike → canonical Latin.
_FOLD: dict[str, str] = {
    # Cyrillic → Latin
    "а": "a",
    "е": "e",
    "о": "o",
    "р": "p",
    "с": "c",
    "у": "y",
    "х": "x",
    "ѕ": "s",
    "і": "i",
    "ј": "j",
    "А": "A",
    "В": "B",
    "Е": "E",
    "К": "K",
    "М": "M",
    "Н": "H",
    "О": "O",
    "Р": "P",
    "С": "C",
    "Т": "T",
    "Х": "X",
    "Ѕ": "S",
    "І": "I",
    "Ј": "J",
    # Greek → Latin
    "α": "a",
    "ο": "o",
    "ν": "v",
    "ρ": "p",
    "τ": "t",
    "χ": "x",
    "υ": "u",
    "Α": "A",
    "Β": "B",
    "Ε": "E",
    "Ζ": "Z",
    "Η": "H",
    "Ι": "I",
    "Κ": "K",
    "Μ": "M",
    "Ν": "N",
    "Ο": "O",
    "Ρ": "P",
    "Τ": "T",
    "Υ": "Y",
    "Χ": "X",
    # Other digits
    "𝟎": "0",
    "𝟏": "1",
    "𝟐": "2",
    "𝟑": "3",
    "𝟒": "4",
    "𝟓": "5",
    "𝟔": "6",
    "𝟕": "7",
    "𝟖": "8",
    "𝟗": "9",
    "Ⅰ": "I",
    "Ⅱ": "II",
    "Ⅲ": "III",
    # Mathematical Latin
    "𝐚": "a",
    "𝐛": "b",
    "𝐜": "c",
    "𝐀": "A",
    "𝐁": "B",
    "𝑎": "a",
    "𝑏": "b",
    "𝒂": "a",
    "𝒃": "b",
}


def _script_name(c: str) -> str:
    """Return Unicode script name (approx via name parsing)."""
    try:
        name = unicodedata.name(c)
    except ValueError:
        return "Unknown"
    if name.startswith("CYRILLIC"):
        return "Cyrillic"
    if name.startswith("GREEK"):
        return "Greek"
    if name.startswith("ARABIC"):
        return "Arabic"
    if name.startswith("HEBREW"):
        return "Hebrew"
    if name.startswith("LATIN"):
        return "Latin"
    if name.startswith("DIGIT") or "MATHEMATICAL" in name:
        return "MathOrDigit"
    return name.split()[0] if name else "Unknown"


def detect(text: str, max_samples: int = 50) -> dict:
    by_pair: Counter = Counter()
    samples: list[dict] = []
    total = 0
    for i, c in enumerate(text):
        if c in _FOLD:
            target = _FOLD[c]
            src = _script_name(c)
            pair = f"Latin-{src}"
            by_pair[pair] += 1
            total += 1
            if len(samples) < max_samples:
                ctx_start = max(0, i - 10)
                ctx_end = min(len(text), i + 10)
                samples.append(
                    {
                        "position": i,
                        "char": c,
                        "codepoint": f"U+{ord(c):04X}",
                        "expected": target,
                        "expected_script": "Latin",
                        "found_script": src,
                        "context": text[ctx_start:ctx_end].replace("\n", " "),
                    }
                )
    return {
        "total_chars": len(text),
        "confusable_hits": total,
        "by_pair": dict(by_pair),
        "samples": samples,
    }


def fold(text: str) -> str:
    """Apply TR39-style fold. USE AS DEDUP KEY ONLY. Never store as canonical."""
    return "".join(_FOLD.get(c, c) for c in text)


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect or fold Unicode confusables.")
    parser.add_argument("input", help="Path to input file or '-' for stdin")
    parser.add_argument("--mode", choices=["detect", "fold"], default="detect")
    parser.add_argument(
        "--use-confusable-homoglyphs",
        action="store_true",
        help="Use the confusable_homoglyphs library for full TR39 fidelity (must be installed)",
    )
    parser.add_argument(
        "--include-joiners",
        action="store_true",
        help="Also detect inconsistent ZWJ/ZWNJ usage (Phase 2+; not implemented in Phase 1)",
    )
    args = parser.parse_args()

    if args.use_confusable_homoglyphs:
        try:
            import confusable_homoglyphs  # noqa: F401
        except ImportError:
            print("ERROR: confusable_homoglyphs not installed. pip install confusable-homoglyphs", file=sys.stderr)
            return 2
        print("WARN: full TR39 path not yet wired; falling back to cached subset", file=sys.stderr)

    if args.include_joiners:
        print("WARN: --include-joiners is Phase 2+; cached path ignores joiners", file=sys.stderr)

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()

    if args.mode == "detect":
        report = detect(raw)
        report["snapshot_date"] = "2026-04-23"
        report["note"] = "Cached TR39 subset. For production, install confusable-homoglyphs."
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 1 if report["confusable_hits"] > 0 else 0
    else:  # fold
        sys.stdout.write(fold(raw))
        return 0


if __name__ == "__main__":
    sys.exit(main())
